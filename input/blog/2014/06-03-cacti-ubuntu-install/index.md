title: Установка Cacti 0.8.8b на Ubuntu Server 14.04
blog: true
template: post.html
datetime: 2014-06-03 14:00
keywords: Cacti, Windows, Linux, Ubuntu, snmp, snmpd, мониторинг
description: Установка Cacti 0.8.8b на Ubuntu Server 14.04.Настройка Windows Linux клиентов.
labels: how-to, windows, ubuntu, мониторинг  
comments: on
---

Cacti - хорошая система мониторинга, которая может собирать информацию по SNMP.   
На момент написания статьи Cacti имеет версию 0.8.8b. Ставить ее будем на `Ubuntu Server 14.04 LTS` - там она уже есть в родном репозитории.


Установка производится очень просто:

`sudo apt-get install cacti`  - дальше менеджер пакетов утащит и настроит все необходимое, вам придется задать пароль root'a и cacti для БД в MySQL и выбрать http-сервер.

## Конфигурация

Cacti уже нормально функционирует "из коробки", ее осталось немножко доконфигурировать.

Можно изменить переодичность запуска пуллера, по дефолту он запускается каждые 5 минут. Если есть необходимость, то меняем интервал в файле `/etc/cron.d/cacti`.

Дабы избежать проблем со временем, конфигурируем PHP на работу с нужной  тайм зоной, для этого отредактируем два файла:

`sudo vim /etc/php5/apache2/php.ini` - для работы PHP c Apache'ем (web-морда)    
`sudo vim /etc/php5/cli/php.ini` - для работы PHP из консоли(пуллер cmd.php)   
И меняем `date.timezone` на необходимую часовую зону, полный список можно посмотреть [тут](http://php.net/date.timezone)

Далее переходим на web-интерфейс `http://cacti.example.com/cacti/` и следуем указаниям мастера.

Выбираем "Новую установку"

![Выбираем тип установки Cacti](/blog/2014/06-03-cacti-ubuntu-install//wi_0.png){: class="thumbnail"}

Проверяем валидность путей к бинарикам и логам

![Проверка путей установки Cacti](/blog/2014/06-03-cacti-ubuntu-install//wi_1.png){: class="thumbnail"}

Входим под учетной записью админа. (стандартный логин/пароль -  admin).

![Вход под администратором Cacti](/blog/2014/06-03-cacti-ubuntu-install//wi_2.png){: class="thumbnail"}

Далее нам в принудительно-добровольном порядке предлагают сменить пароль, что мы и сделаем. Cacti готова к использованию! :)

Я, лично, не представляю себе систему мониторинга без оповещения проблем по E-mail'у.

Для это нам понадобятся плагины [thold](http://docs.cacti.net/plugin:thold) и [settings](http://docs.cacti.net/plugin:settings). Начиная с Cacti 0.8.8a  Plugin Architecture стала частью Cacti, что очень хорошо, и упростит установку плагинов.   
Скачаем плагины по ссылкам сверху, распакуем в директорию `/usr/share/cacti/site/plugins/` и заходим на web-морду **Console->Plugin Management**. Устанавливаем и активируем их.

![Список установленных плагинов](/blog/2014/06-03-cacti-ubuntu-install//wi_3.png)

Далее идем в **Console->Setting->Mail/DNS** и настраиваем отправку почты (я настроил через SMTP сервер)

![Настройка уведомлений по электронной почте Cacti](/blog/2014/06-03-cacti-ubuntu-install//wi_4.png)

Продолжаем в **Console->Setting->Thresholds**. Включаем `Dead Hosts Notifications` (уведомление в случае падения/поднятия хоста) и прописываем e-mail'ы для уведомлний. Тут пока можно заканчивать.

Забыл сказать, что с помощью `thold` можно создавать трэшхолды, вешать на них уведомления по почте, но это я оставлю вам, там ни чего сложного нет ;)

## Клиенты для мониторинга

### Windows хосты

* На Windows Server устанавливаем компонент `Служба SNMP`
* Заходим в оснастку управления службами, ищем Службу SNMP -> Свойства -> Безопасность. Добавляем новое коммьюнити и адресс нашего cacti-сервера.    
![Настройка SNMP Windows Server 2008 R2](/blog/2014/06-03-cacti-ubuntu-install//win_0.png)
* На вкладке Агент SNMP выставлем все службы и вносим данные о контактном лице и расположении   
![Настройка SNMP Windows Server 2008 R2](/blog/2014/06-03-cacti-ubuntu-install//win_1.png)

Теперь нам нужно установить `SNMP Informant Standard Metrics for Windows Devices` для удобного сбора данных с Windows устройств. Страничка автора проекта на [гитхабе](https://github.com/mrlesmithjr/cacti).

* Скачиваем [отсюда](http://www.snmp-informant.com/snmp_informant-standard.htm) SNMP Informant-STD и устанавливаем на Windows Server
* Скачиваем со странички автора [архив](https://github.com/mrlesmithjr/cacti/archive/master.zip) с шаблонами и ресурсами.
* Файлы `resource\snmp_queries\snmp_informant_standard_*.xml` копируем в `/usr/share/cacti/site/resource/snmp_queries/`
* Шаблоны из `template\*` импортируем через web-интерфейс Сacti **Console->Import Templates**

Теперь можно добавлять Windows хосты!

* **Console->Devices->Add** и выбираем *Host Template* `SMNP_Informant_Windows`
![Выбор шаблона Windows для Cacti](/blog/2014/06-03-cacti-ubuntu-install//win_2.png)   

### GNU/Linux Ubuntu хосты

* Устанавливаем SNMPD   
`sudo apt-get install snmpd`  
* Редактируем конфиг `/etc/snmp/snmpd.conf` по минимуму    
```text
agentAddress  udp:161
rocommunity public  x.x.x.x # где x.x.x.x - ip адрес cacti-сервера
```
* Перезапускаем snmpd `sudo /etc/init.d/snmpd restart`
* Добавляем новый linux девайс

Активное сетевое оборудование добавляет подобным же образом:
* Конфигурируем SNMP агент на железке
* Новое устройство добавлем в Cacti

А теперь добавляем графики, трэшхолды и наслаждаемся ;)

**P.S.**:*Естественно, данное руководство не может считаться полным по конфигурированию Cacti и SNMP-агентов на разных платформах, а также не подходит на истину в последней инстанции*