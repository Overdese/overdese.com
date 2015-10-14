title: Установка Java на Ubuntu 14.04
blog: true
template: post.html
datetime: 2014-07-31 14:49
keywords: ubuntu, java, jre, jdk, openjdk, openjre
description: Как установить Java на Ubuntu Linux клиентов.
labels: ubuntu, how-to  
comments: on
---

## JRE или JDK

Прежде чем установить java, давайте посмотрим что такое JRE, OpenJDK и OracleJDK, и определимся, что нам нужно.

* *JRE (Java Runtime Environment)* - это то, что нужно вам для нормального запуска Java-приложений, это минимум и максим для обычного пользователя.
* *JDK (Java Development Kit)*  - это то что нужно для разработки приложений на Java.

OracleJDK - официальная версия JDK от Oracle, в то время, как OpenJDK - это реализация JDK с открытым исходным кодом. OpenJDK хватает для большинства случаев, однако, все же рекомендую использовать OracleJDK.

<!-- more -->

![Как установить java на ubuntu?](/blog/2014/07-31-java-ubuntu-install/main.jpg){: class="thumbnail"}

## Установлена ли Java?

Для проверки наличия Java в системе достаточно открыть терминал и выполнить:  
`java -version`  
Если вывод команды должен показать вам версию приложения установленного в системе, если нам ответили что ни чего подобного в системе нет - значит самое время ее установить!

# Установка JRE

Для установки JRE нам достаточно в терминале вбить и дождаться выполнения команды.  
`sudo apt-get install default-jre`

# Установка OpenJDK

Установка не отличается сложностью от JRE:  
`sudo apt-get install default-jdk`

 Однако, если вам нужна определенная версия версия Java, то вы можете использовать openjdk-6-jdk/jre и openjdk-6-jdk/jre соответсвенно.

# Установка OracleJDK

С установкой официальной JDK от Oracle немного посложненее, но не сильно

* подключаем репозиторий  
`sudo add-apt-repository ppa:webupd8team/java`  
* `sudo apt-get update`  
* и устанавливаем  
`sudo apt-get install oracle-java8-installer`

Естественно, если вам нужна Java7, то меняет java8 на java7 в последней команде.
