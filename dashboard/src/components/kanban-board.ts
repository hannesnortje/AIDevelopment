import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('kanban-board')
export class KanbanBoard extends LitElement {
    @property({ type: Array }) tickets: any[] = [];

    static styles = css`
    :host {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      height: 100%;
      overflow: hidden;
    }
    .column {
      background: #2a2a2a;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    .column-header {
      padding: 10px;
      background: #333;
      border-radius: 8px 8px 0 0;
      font-weight: bold;
      text-transform: uppercase;
      font-size: 0.8rem;
    }
    .ticket-list {
      padding: 10px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .ticket-card {
      background: #3a3a3a;
      padding: 10px;
      border-radius: 4px;
      border-left: 3px solid #007bff;
      font-size: 0.9rem;
    }
    .ticket-title {
      font-weight: bold;
      margin-bottom: 5px;
    }
    .ticket-meta {
      font-size: 0.75rem;
      color: #999;
      display: flex;
      justify-content: space-between;
    }
    .type-bug { border-left-color: #ff4444; }
    .type-chore { border-left-color: #ffbb33; }
  `;

    render() {
        const columns = ['draft', 'approved', 'in_progress', 'review', 'done'];

        return html`
      ${columns.map(status => html`
        <div class="column">
          <div class="column-header">${status.replace('_', ' ')}</div>
          <div class="ticket-list">
            ${this.tickets
                .filter(t => t.status === status)
                .map(t => html`
                <div class="ticket-card type-${t.type}">
                  <div class="ticket-title">${t.title}</div>
                  <div class="ticket-meta">
                    <span>${t.id}</span>
                    <span>${t.assigned_to || '-'}</span>
                  </div>
                </div>
              `)}
          </div>
        </div>
      `)}
    `;
    }
}
