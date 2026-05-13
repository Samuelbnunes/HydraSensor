import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PubNub from 'pubnub';
import { LogOut, Activity } from 'lucide-react';
import EventCard, { RFIDEvent } from '../../components/EventCard/EventCard';
import Button from '../../components/Button/Button';
import styles from './Dashboard.module.css';

const PUBNUB_SUBSCRIBE_KEY = 'sub-c-7830b8bc-9ccc-4f70-b89d-0a22951b20a8';
const PUBNUB_CHANNEL = 'meu_canal';

const Dashboard: React.FC = () => {
  const [events, setEvents] = useState<RFIDEvent[]>([]);
  const [connectionStatus, setConnectionStatus] = useState('Conectando...');
  const [isConnected, setIsConnected] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Buscar histórico inicial do backend
    const fetchHistory = async () => {
      try {
        const res = await fetch('/v1/access-events');
        const data = await res.json();
        if (res.ok && data.data && Array.isArray(data.data)) {
          setEvents(data.data);
        }
      } catch (err) {
        console.error('Erro ao buscar histórico inicial', err);
      }
    };

    fetchHistory();

    // Configurar realtime com PubNub
    const pubnub = new PubNub({
      subscribeKey: PUBNUB_SUBSCRIBE_KEY,
      userId: 'rfid-dashboard-react',
    });

    pubnub.addListener({
      status: (statusEvent) => {
        if (statusEvent.category === 'PNConnectedCategory') {
          setConnectionStatus('Conectado em tempo real');
          setIsConnected(true);
        } else if (statusEvent.category === 'PNDisconnectedCategory') {
          setConnectionStatus('Desconectado');
          setIsConnected(false);
        }
      },
      message: (messageEvent) => {
        const event = messageEvent.message.data as RFIDEvent;
        if (event) {
          setEvents((prevEvents) => [event, ...prevEvents]);
        }
      },
    });

    pubnub.subscribe({ channels: [PUBNUB_CHANNEL] });

    return () => {
      pubnub.unsubscribeAll();
    };
  }, []);

  const handleLogout = () => {
    navigate('/login');
  };

  const latestEvent = events[0];
  const historyEvents = events.slice(1);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.logoWrapper}>
            <Activity size={24} className={styles.logoIcon} />
          </div>
          <div>
            <h1 className={styles.title}>Monitor de Acessos</h1>
            <div className={styles.statusWrapper}>
              <span className={isConnected ? styles.statusDotConnected : styles.statusDotDisconnected} />
              <span className={styles.statusText}>{connectionStatus}</span>
            </div>
          </div>
        </div>
        <Button variant="secondary" onClick={handleLogout} className={styles.logoutBtn}>
          <LogOut size={16} />
          <span>Sair</span>
        </Button>
      </header>

      <main className={styles.main}>
        <div className={styles.grid}>
          {/* Coluna da Última Leitura */}
          <section className={styles.latestSection}>
            <h2 className={styles.sectionTitle}>Última Leitura</h2>
            {latestEvent ? (
              <EventCard event={latestEvent} highlight />
            ) : (
              <div className={styles.emptyState}>
                <Activity size={48} className={styles.emptyIcon} />
                <p>Aguardando aproximação da tag...</p>
              </div>
            )}
          </section>

          {/* Coluna de Histórico */}
          <section className={styles.historySection}>
            <h2 className={styles.sectionTitle}>Histórico de leituras</h2>
            <div className={styles.historyList}>
              {historyEvents.length > 0 ? (
                historyEvents.map((ev, index) => (
                  <EventCard key={`${ev.tag_id}-${index}`} event={ev} />
                ))
              ) : (
                <div className={styles.emptyStateSmall}>
                  <p>Nenhum evento anterior registrado.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
