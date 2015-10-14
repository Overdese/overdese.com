title: Перевод рабочих станций на динамическое получение IP-адресов
blog: true
template: post.html
datetime: 2014-03-25 09:00
keywords: DHCP, Microsoft, IP-адрес, скрипты, vbs, Active Directory, переход
description: Переход на DHCP
labels: active directory, how-to, windows  
comments: on
---

В одной организации появилась необходимость смены IP-адресации(была 192 сеть, должна стать 10-ой). Исторически сложилось так, что клиентские машины (порядка 500 штук) имели статически-выданные IP-адреса, которые закреплялись за каждой машиной. Для упрощения "переползания" в другую сеть было решено развернуть DHCP-сервер в новой сети (Dynamic Host Configuration Protocol), создать минимум 2 области (на каждую из сетей), выполнить резервирование для клиентских машин (на тот момент для клиентской машины было много завязано на IP-адрес), настроить их на получение IP-адреса средствами DHCP и в определенный момент (в конце рабочего дня, например) достаточно перекоммутировать в новую сеть оборудование и с утра клиентские машины, незаметно для пользователей, окажутся уже в новой подсети. Так же необходимо будет настроить DHCP Relay на роутере, маршрутизирующего старую и новую сеть.


![Визуальная схема](/blog/2014/03-25-auto-dhcp/main.jpg){: class="thumbnail"}


Начнем с разворачивание DHCP-сервера. Думаю с этим проблем возникнуть не должно. Копипастить инструкцию не буду, все можно найти в [документации на оффсайте Microsoft'a](http://technet.microsoft.com/ru-ru/windowsserver/dd448608.aspx)   
Создаем две области - одну для 10-сети, другую для 192-сети, задаем необходимые параметры области, и выделяем диапазон адресов для выдачи, такой, чтобы не пресекался с адресами наших машин. Проверяем работу DHCP-сервера, если все ок - переходим к настройке DHCP relay. Настройка опции зависит от роутера, используемого для маршрутизации сетей. В данном случаe, в качестве роутера использовался сервер под управлением Windows Server 2003. Настройка не сложная, [офф.документация доступна здесь](http://technet.microsoft.com/ru-ru/library/dd469685.aspx). Проверяем работу DHCP Relay'я, думю что все будет ок ;)

Следующий шаг достаточно рутинный - нам нужно перенастроить клиентские машины на получения IP-адреса, а их напомню не мало - порядка 500 штук. Конечно можно занятся физподготовкой и пробежать все компы ножками и настроить ручками, так же не стоит забывать, нам нужно, чтобы IP-адреса остались за машинами - а это значит, что нам нужно добавить на каждую машину резервирование по MAC'у.   
Но это не наш метод, когда можно все автоматизировать, особенно когда есть Active Directory с групповыми политиками.    

План такой:  

1. собираем скриптом при загрузке машины необходимую инфу, а именно IP'шники и соответсвующие им MAC'и
2. делаем скрипт для резервирования адресов на основе добытой инфы
3. включаем на клиентах DHCP-клиент и перенастраиваем сетевые интерфейсы
4. ????
5. Profit!

Поехали!    
 
Создадим vbs-скрипт ip-reserv.vbs и копируем его в любое доступное место в сети (например, директория Netlogon на контроллере домена):

```
On Error Resume Next
Dim IPADDRES, strMacAddress, strHostname
Dim WshShell
Dim fso, tf

strComputer = "."
Set objWMIService = GetObject("winmgmts:" _
 & "{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")
Set colNicConfigs = objWMIService.ExecQuery _
 ("SELECT * FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled = True")

Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell=CreateObject("WScript.Shell")


For Each obj in colNicConfigs
  strHostname = obj.DNSHostName
Next

Set tf = fso.CreateTextFile("\\Server\Share\statinfo\dhcp\reserv-" & strHostname & ".txt", True)

For Each objNicConfig In colNicConfigs
      For Each strIPAddress In objNicConfig.IPAddress        
       strMacAddress = Replace(objNicConfig.MACAddress, ":", "")
       tf.WriteLine("netsh dhcp server \\10.10.0.1 Scope 192.168.0.0 Add reservedip " & strIPAddress & " " & strMacAddress & " " & strHostname)
       
      Next
Next

tf.Close

Set WshShell = Nothing
WScript.Quit

```


Где, `Server` - имя сервера на который будут складываться "отчеты", `10.10.0.1` - IP-адрес DHCP-сервера, `192.168.0.0` - имя области на DHCP-сервере.  
Создаем объект групповой политики, где в автозагрузку ставим наш скрипт и применем его к подразделениям с нашими машинками. Теперь достаточно <s>одной таблэтки</s> перезагрузки для каждой машинки и вся нужная инфа у нас будет.     
Далее можно склеить все файлы в один большой и перебить расширения на bat, запускаем и... тадааам, все зарезервировано. При переползании в другую подсеть с "сохранением IP'шника" достаточно, открыть наш bat'ник продвинутым текстовым редактором и заменить все вхождения 192.168. на 10.10..

Создаем новый объект групповой политики и так же применяем на нужные подразделения, в котором включаем службу DHCP-клиент и добавляем новый скрипт в автозагрузку - dhcp_set.vbs:


```
strComputer = "."
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
Set colNetAdapters = objWMIService.ExecQuery _
("Select * from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE")
For Each objNetAdapter In colNetAdapters
errDhcpEnable = objNetAdapter.EnableDHCP()
errDnsAuto = objNetAdapter.SetDNSServerSearchOrder()
'If errEnable = 0 Then
'Wscript.Echo "DHCP has been enabled."
'Else
'Wscript.Echo "DHCP could not be enabled."
'End If
'If errDnsAuto = 0 Then
'Wscript.Echo "Auto DNS has been enabled."
'Else
'Wscript.Echo "Auto DNS could not be enabled."
'End If
Next
```


При следующей загрузке клиентские машинки будут "сидеть" на DHCP.

Дальше все давольно-таки просто - постепенно перекидываем оборудование из старой сети в новую и наступает щастье.

P.S. я нарочно опустил планирование и "развертывание" новой сети ибо это тема для болшой статьи и эта статья не о том.