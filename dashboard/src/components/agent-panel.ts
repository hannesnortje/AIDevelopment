import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('agent-panel')
export class AgentPanel extends LitElement {
    @property({ type: Object }) agents: any = {};

    static styles = css`
    :host {
      background: #252525;
      border-right: 1px solid #333;
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 10px;
      overflow-y: auto;
    }
    h3 { margin: 0 0 10px 0; font-size: 1rem; color: #888; }
    .agent-card {
      background: #333;
      padding: 10px;
      border-radius: 4px;
      border: 1px solid #444;
    }
    .agent-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 5px;
    }
    .agent-role {
      font-weight: bold;
      font-size: 0.9rem;
    }
    .status-badge {
      font-size: 0.7rem;
      padding: 2px 6px;
      border-radius: 10px;
      background: #555;
    }
    .status-working { background: #28a745; color: white; }
    .status-idle { background: #ffc107; color: black; }
    .status-error { background: #dc3545; color: white; }
    
    .current-task {
      font-size: 0.8rem;
      color: #aaa;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  `;

    render() {
        return html`
      <h3>Team Agents</h3>
      ${Object.entries(this.agents).length === 0
                ? html`<div style="color:#666">No agents active</div>`
                : ''}
        
      ${Object.values(this.agents).map((agent: any) => html`
        <div class="agent-card">
          <div class="agent-header">
            <span class="agent-role">${agent.role}</span>
            <span class="status-badge status-${agent.state}">${agent.state}</span>
          </div>
          <div class="current-task">
            ${agent.current_ticket ? `Ticket #${agent.current_ticket}` : 'Waiting for tasks...'}
          </div>
        </div>
      `)}
    `;
    }
}
