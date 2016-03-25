# openstack-nas-configurator

Здесь содержится скрипт, который осуществляет конфигурацию OpenStack и NAS сервера, для предоставления сервисов VM, созданных в OpenStack.


https://github.com/mariashko/openstack-nas-configurator-scripts - скрипты, которые нужно положить в nas-srv-et/nas-srv-et-scripts на сервере


<b>Конфигурируется все это следующим образом:</b>

В services.cfg в первой строчке должен быть список сервисов через пробел. Там же будут появляться записи вида "сервис ip название_subnet\n" для подключенных сервисов.
В server.cfg надо прописать ip сервера и path к папке nas-srv-et.
В gen_cfg.py можно поменять port, transport, qlen для генерации конфига(server_config.cfg) nas-server.

<b>Перед первым запуском должен быть запущен ./init_server.</b>



У ./main.py есть следующие опции: subnet-list, service-list, join <subnet> <service>, delete <service>.


<b>Subnet-list</b> показывает список, который есть у neutron.

<b>Service-list</b> парсит services.cfg и отображает информацию оттуда.

<b>Join \<subnet\> \<service\></b> 

  1. находит и убирает из allocation_pools subnet IP-address
  2. добавляет запись к services.cfg
  3.по ssh на сервере: добавляет namespace, vlan-dev и пр. для сервиса с помощью add_serv.sh, переписывает server_config.cfg с помощью gen_cfg.py и перезапускает сервер

<b> Delete \<service\> </b>

  1. убирает запись из services.cfg
  2. возвращает IP в allocation_pools subnet
  3. по ssh на сервере: удаляет namespace, vlan-dev и пр. сервиса с помощью del_serv.sh, переписывает server_config.cfg с помощью gen_cfg.py и перезапускает сервер
