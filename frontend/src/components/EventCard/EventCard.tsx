import React from 'react';
import clsx from 'clsx';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';
import styles from './EventCard.module.css';

export interface RFIDEvent {
  nome: string;
  evento: string;
  autorizado: boolean;
  tag_id: string;
  mensagem: string;
  lido_em: string;
}

interface EventCardProps {
  event: RFIDEvent;
  highlight?: boolean;
}

const EventCard: React.FC<EventCardProps> = ({ event, highlight = false }) => {
  return (
    <div className={clsx(styles.card, highlight && styles.highlight)}>
      <div className={styles.header}>
        <div className={styles.titleWrapper}>
          <span className={styles.title}>{event.nome}</span>
          <span className={styles.subtitle}>{event.evento}</span>
        </div>
        <div className={clsx(styles.badge, event.autorizado ? styles.badgeSuccess : styles.badgeDanger)}>
          {event.autorizado ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
          <span>{event.autorizado ? 'Autorizado' : 'Negado'}</span>
        </div>
      </div>
      
      <div className={styles.body}>
        <div className={styles.infoRow}>
          <span className={styles.label}>Tag ID:</span>
          <span className={styles.value}>{event.tag_id}</span>
        </div>
        <div className={styles.infoRow}>
          <span className={styles.label}>Mensagem:</span>
          <span className={styles.value}>{event.mensagem}</span>
        </div>
      </div>
      
      <div className={styles.footer}>
        <Clock size={14} className={styles.timeIcon} />
        <span className={styles.timeText}>{event.lido_em}</span>
      </div>
    </div>
  );
};

export default EventCard;
