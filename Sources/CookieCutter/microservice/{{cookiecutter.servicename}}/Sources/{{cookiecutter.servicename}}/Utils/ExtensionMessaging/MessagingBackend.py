from confluent_kafka import Producer, Consumer
# from confluent_kafka.admin import AdminClient
# from confluent_kafka.cimpl import NewPartitions
from kombu import Exchange, Queue, Connection
import redis

from Utils.Core.BaseObject import BaseObject
from Utils.Exception.MessagingException import MessagingException
from Utils.Core.Singleton import Singleton
from Utils.Errors.MessagingError import *


class MessagingBackend(BaseObject, Singleton):
    MSG_BACKEND_SETTINGS = {
        'Mandatory': ['URL', 'MaxConnections'],
        'Optional': []
    }
    EXCHANGE_SETTINGS = {
        'Mandatory': ['Type', 'MessagingBackend'],
        'Optional': []
    }
    QUEUE_SETTINGS = {
        'Mandatory': ['Exchange', 'RoutingKey'],
        'Optional': ['ResultsQueue', 'AsyncJobStore']
    }
    DATASTORE_BACKEND = {
        'Mandatory': ['Host', 'Port', 'DB', 'Password', 'MaxConnections'],
        'Optional': []
    }

    def __init__(self):
        BaseObject.__init__(self)

        self._BackendSpecName = None
        self._MessagingBackend = dict()
        self._Exchanges = dict()
        self._Queues = dict()
        self._DataStoreBackend = dict()

    def setup(self, backend_spec_name='BackendManager'):
        """
        Sets up the entire backend messaging connections and initial setup based on the definition available in the
        configuration section of the project
        Args:
            backend_spec_name: section name in the conf file

        Returns:

        """
        self._BackendSpecName = backend_spec_name

        backend_manager_settings = self._config_manager.get_settings(self._BackendSpecName)

        # Get Messaging Backend Settings from Configuration File
        specifications = backend_manager_settings.get('MessagingBackends')
        if specifications:
            specs = [value.strip() for value in specifications.split(',')]
            for spec in specs:
                # Set up the Backend Connections
                self._setup_messaging_backend(spec)

        # Get Exchange Settings from Configuration File
        specifications = backend_manager_settings.get('Exchanges')
        if specifications:
            specs = [value.strip() for value in specifications.split(',')]
            for spec in specs:
                # Set up the exchanges
                self._setup_exchange(spec)

        # Get Queues Settings from Configuration File
        specifications = backend_manager_settings.get('Queues')
        if specifications:
            specs = [value.strip() for value in specifications.split(',')]
            for spec in specs:
                # Setup the Queues
                self._setup_queue(spec)

        # Get DataStore Settings from Configuration File
        specifications = backend_manager_settings.get('DataStoreBackends')
        if specifications:
            specs = [value.strip() for value in specifications.split(',')]
            for spec in specs:
                # Set up the datastore
                self._setup_datastore_backend(spec)

    def _setup_messaging_backend(self, messaging_backend_setting):
        """
        Sets up the Backend Manager based on the URL
        Kombu supports both AMQP and REDIS
        Heartbeat to check if the connection is alive
        Connection is stored in the self._MessagingBackend dict

        Args:
            messaging_backend_setting (object): Messaging Queue setting
        """
        settings = self._config_manager.get_settings(messaging_backend_setting)
        for setting_name in self.MSG_BACKEND_SETTINGS['Mandatory']:
            if setting_name not in settings:
                raise MessagingException(MESSAGING_BACKEND_SETTING_NOT_FOUND, setting_name, messaging_backend_setting)

        if messaging_backend_setting in self._MessagingBackend:
            return

        self._MessagingBackend[messaging_backend_setting] = dict()
        self._MessagingBackend[messaging_backend_setting]['Settings'] = settings
        # heartbeat = 0
        url = settings['URL']
        transport = settings['TRANSPORT']
        # maxConnection = int(settings['MaxConnections'])
        # if settings.get('heartbeat'):
        #    heartbeat = int(settings['heartbeat'])
        if transport == 'kafka':
            conn = settings['URL']
        else:
            conn = Connection(url)  # , heartbeat)
        # conn.ensure_connection()
        self._MessagingBackend[messaging_backend_setting]['Connection'] = conn

    def _setup_exchange(self, exchange_setting):
        """
        Sets up the Exchange in the Messaging / DataStore 
        If Exchange is not available it will automatically create the exchange information 
        as per the definition in the settings configuration of the app
        If Backend is not available it will automatically create the backend connection
        A dummy queue is inserted to the messaging / datastore once the exchange is created for testing

        Args:
            exchange_setting: exchange related setting
        """
        settings = self._config_manager.get_settings(exchange_setting)
        for setting_name in self.EXCHANGE_SETTINGS['Mandatory']:
            if setting_name not in settings:
                raise MessagingException(MESSAGING_BACKEND_SETTING_NOT_FOUND, setting_name, exchange_setting)

        if exchange_setting in self._Exchanges:
            return

        self._Exchanges[exchange_setting] = dict()
        self._Exchanges[exchange_setting]['Settings'] = settings

        exchange_type = settings['Type']
        messaging_backend_setting = settings['MessagingBackend']

        self._setup_messaging_backend(messaging_backend_setting)

        if exchange_type == 'direct':
            exchange = Exchange(exchange_setting, type=exchange_type)
            conn = self.get_backend_connection(messaging_backend_setting)
            bound_exchange = exchange(conn)

            dummy_queue = Queue(('%s-DummyQueue' % exchange_setting), bound_exchange)
            dummy_queue(conn).declare()

        else:
            exchange = None

        self._Exchanges[exchange_setting]['ExchangeObject'] = exchange

    def _setup_queue(self, queue_setting):
        """
        Sets up the Queue in the Exchange
        If Queue is not available it will automatically create the queue information 
        as per the definition in the settings configuration of the app
        If Exchange is not available it will automatically create the exchange connection

        Args:
            queue_setting: Queue settings
        """
        settings = self._config_manager.get_settings(queue_setting)
        for setting_name in self.QUEUE_SETTINGS['Mandatory']:
            if setting_name not in settings:
                raise MessagingException(MESSAGING_BACKEND_SETTING_NOT_FOUND, setting_name, queue_setting)

        if queue_setting in self._Queues:
            return

        self._Queues[queue_setting] = dict()
        self._Queues[queue_setting]['Settings'] = settings

        exchange_setting = settings['Exchange']
        routing_key = settings['RoutingKey']
        exc_settings = self._config_manager.get_settings(exchange_setting)
        self._setup_exchange(exchange_setting)

        exchange_object, conn = self.get_exchange(exchange_setting)
        if exc_settings['Type'] == 'direct':
            queue_object = Queue(queue_setting, exchange_object, routing_key)

            simple_queue_object = conn.SimpleQueue(queue_object)
            self._Queues[queue_setting]['QueueObject'] = simple_queue_object
        else:
            group = settings['ConsumerGroup']
            # partitions = int(settings['Partitions'])
            # replicas = int(settings['Replicas'])
            bootstrap_servers = {
                'bootstrap.servers': conn,
                'acks': 'all'
            }
            producer = Producer(bootstrap_servers)

            # kafka_admin = AdminClient(bootstrap_servers)
            # available_topics = kafka_admin.list_topics(routing_key.split(',')[0])
            # if len(available_topics.topics[routing_key.split(',')[0]].partitions) != partitions:
            #     _partition = NewPartitions(routing_key, partitions)
            #     kafka_admin.create_partitions([_partition])
            #     # _topic = []
            #     # for keys in routing_key.split(','):
            #     #     _topic.append(kafka_admin.NewTopic(keys, partitions, replicas))
            #     # kafka_admin.create_topics(_topic)

            settings = {
                'bootstrap.servers': conn,
                'group.id': group,
                'enable.auto.commit': True,
                'session.timeout.ms': 6000,
                'default.topic.config': {'auto.offset.reset': 'earliest'}
            }
            consumer = Consumer(settings)

            if isinstance(routing_key, str):
                consumer.subscribe([keys.strip() for keys in routing_key.split(',')])
            elif isinstance(routing_key, list):
                consumer.subscribe(routing_key)
            else:
                raise MessagingException(MESSAGING_BACKEND_SETTING_NOT_FOUND, settings, queue_setting)

            self._Queues[queue_setting]['ProducerObject'] = producer
            self._Queues[queue_setting]['ConsumerObject'] = consumer
            self._Queues[queue_setting]['TopicList'] = routing_key

    def _setup_datastore_backend(self, data_store_setting):
        """
        Sets up the Backend Manager based on the URL
        Kombu supports both AMQP and REDIS
        Heartbeat to check if the connection is alive
        Connection is stored in the self._MessagingBackend dict

        Args:
            data_store_setting (object): data store settings
        """
        settings = self._config_manager.get_settings(data_store_setting)
        for setting_name in self.DATASTORE_BACKEND['Mandatory']:
            if setting_name not in settings:
                raise MessagingException(MESSAGING_BACKEND_SETTING_NOT_FOUND, setting_name, data_store_setting)

        if data_store_setting in self._DataStoreBackend:
            return

        self._DataStoreBackend[data_store_setting] = dict()
        max_connections = int(settings['MaxConnections'])
        # connection = Connection(hostname=settings['Host'], port=settings['Port'], db=settings['DB'],
        #                         password=settings['Password'])
        self._DataStoreBackend[data_store_setting]['Settings'] = settings

        self._DataStoreBackend[data_store_setting]['ConnectionPool'] = \
            redis.ConnectionPool(host=settings['Host'],
                                 port=settings['Port'],
                                 db=settings['DB'],
                                 max_connections=max_connections)

    def teardown(self):
        """
        Tear down events for disposing all settings
        """
        self._teardown_messaging_backend()
        self._teardown_exchange()
        self._teardown_queue()
        self._teardown_datastore_backend()

    def _teardown_messaging_backend(self, messaging_backend_setting=None):
        """
        Closes / deletes the messaging connection

        Args:
            messaging_backend_setting (object): Messaging Queue setting
        """
        if messaging_backend_setting:
            backend = [messaging_backend_setting]
        else:
            backend = list(self._MessagingBackend.keys())

        for messaging_backend_setting in backend:
            setting = self._MessagingBackend[messaging_backend_setting]
            if setting:
                conn = setting.get('Connection')
                if conn and type(conn) != str:
                    conn.release()

    def _teardown_exchange(self, exchange_setting=None):
        """
        Closes / deletes the exchange connection

        Args:
            exchange_setting (object): exchange settings
        """
        if exchange_setting:
            backend = [exchange_setting]
        else:
            backend = list(self._Exchanges.keys())

        for exchange_setting in backend:
            setting = self._Exchanges[exchange_setting]
            if setting:
                exchange_object = setting.get('ExchangeObject')
                if exchange_object and exchange_object is not None:
                    exchange_object.delete(True, False)  # Delete exchange if no bindings

    def _teardown_queue(self, queue_setting=None):
        """
        Closes / deletes the queue

        Args:
            queue_setting (object): Queue settings
        """
        if queue_setting:
            backend = [queue_setting]
        else:
            backend = list(self._Queues.keys())

        for queue_setting in backend:
            setting = self._Queues[queue_setting]
            if setting and 'QueueObject' in setting:
                queue_object = setting.get('QueueObject')
                if queue_object:
                    queue_object.close()
            if setting and 'ProducerObject' in setting:
                queue_object = setting.get('ProducerObject')
                if queue_object:
                    queue_object.flush()
            if setting and 'ConsumerObject' in setting:
                queue_object = setting.get('ConsumerObject')
                if queue_object:
                    queue_object.flush()

    def _teardown_datastore_backend(self, data_store_setting=None):
        """
        Closes / deletes the queue

        Args:
            data_store_setting (object): Data store settings
        """
        if data_store_setting:
            backend = [data_store_setting]
        else:
            backend = list(self._DataStoreBackend.keys())

        for data_store_setting in backend:
            setting = self._DataStoreBackend[data_store_setting]
            if setting:
                conn_pool = setting.get('ConnectionPool')
                if conn_pool:
                    conn_pool.disconnect()

    def get_backend_connection(self, messaging_backend_setting, backend_type=''):
        """
        Get the backend connection from the Messaging Connection list If messaging setting or id is not available it
        will create the messaging connection and return the connection object

        Args:
            backend_type: type of the messaging direct/kafka
            messaging_backend_setting (object): Messaging Queue setting
        """
        if messaging_backend_setting not in self._MessagingBackend:
            self._setup_messaging_backend(messaging_backend_setting)

        if backend_type == 'kafka':
            return self._MessagingBackend[messaging_backend_setting].get('Connection')

        return_connection = self._MessagingBackend[messaging_backend_setting].get('Connection')

        return_connection.ensure_connection(max_retries=5, interval_step=2)
        return return_connection

    def release_backend_connection(self, messaging_backend_setting, conn):
        """
        Releases the established connection from the pool

        Args:
            conn: connection object
            messaging_backend_setting (object): Messaging Queue setting
        """
        if messaging_backend_setting not in self._MessagingBackend:
            self._setup_messaging_backend(messaging_backend_setting)

        connection_pool = self._MessagingBackend[messaging_backend_setting].get('ConnectionPool')

        if connection_pool:
            try:
                connection_pool.release(conn)
            except Exception as ex:
                self._Logger.error('Cannot release connection from connection pool. Details - %s' % str(ex))

    def get_queue(self, queue_setting_key):
        """
        Return the Queue, Exchange, Connection object from the pool which are matching the queue_setting
        If queue is not available it will automatically create it

        Args:
            queue_setting_key (object): queue name
        """
        if queue_setting_key not in self._Queues:
            self._setup_queue(queue_setting_key)

        if 'QueueObject' in self._Queues[queue_setting_key]:
            queue_object = self._Queues[queue_setting_key].get('QueueObject')
            queue_setting = self._Queues[queue_setting_key].get('Settings')

            exchange_key = queue_setting.get('Exchange')
            if exchange_key not in self._Exchanges:
                self._setup_exchange(exchange_key)

            exchange_object, connection_object = self.get_exchange(exchange_key)

            return None, queue_object, exchange_object, connection_object
        elif 'ProducerObject' in self._Queues[queue_setting_key]:
            producer_object = self._Queues[queue_setting_key].get('ProducerObject')
            consumer_object = self._Queues[queue_setting_key].get('ConsumerObject')
            topics_list = self._Queues[queue_setting_key].get('TopicList')

            queue_setting = self._Queues[queue_setting_key].get('Settings')

            exchange_key = queue_setting.get('Exchange')
            if exchange_key not in self._Exchanges:
                self._setup_exchange(exchange_key)

            exchange_object, connection_object = self.get_exchange(exchange_key)

            return topics_list, producer_object, consumer_object, connection_object

    def get_exchange(self, exchange_key):
        """
        Return the Exchange, Connection object from the pool which are matching the exchange_key
        If Exchange is not available it will automatically create it

        Args:
            exchange_key (object): exchange name
        """
        if exchange_key not in self._Exchanges:
            self._setup_exchange(exchange_key)

        exchange_object = self._Exchanges[exchange_key].get('ExchangeObject')
        exchange_setting = self._Exchanges[exchange_key].get('Settings')
        messaging_backend_setting = exchange_setting.get('MessagingBackend')

        if messaging_backend_setting not in self._MessagingBackend:
            self._setup_messaging_backend(messaging_backend_setting)

        connection_object = self.get_backend_connection(messaging_backend_setting, exchange_setting['Type'])

        return exchange_object, connection_object

    def get_datastore_backend_connection(self, datastore_setting_key):
        """
        Get the backend connection from the Messaging Connection list If messaging setting or id is not available it
        will create the messaging connection and return the connection object

        Args:
            datastore_setting_key (object): data store name
        """
        if datastore_setting_key not in self._DataStoreBackend:
            self._setup_datastore_backend(datastore_setting_key)

        datastore_connection_pool = self._DataStoreBackend[datastore_setting_key].get('ConnectionPool')
        datastore_setting = self._DataStoreBackend[datastore_setting_key].get('Settings')

        return datastore_connection_pool, datastore_setting
