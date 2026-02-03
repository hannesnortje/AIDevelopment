import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { wsService } from './services/websocket';
import './components/kanban-board';
import './components/agent-panel';

@customElement('dashboard-app')
export class DashboardApp extends LitElement {
    @state() connected = false;
    @state() projectState: any = null;
    @state() configMode = true;
    @state() concept = 'Create a todo app with Lit 3';

    static styles = css`
    :host {
      display: block;
      height: 100vh;
      display: grid;
      grid-template-rows: 60px 1fr;
    }
    header {
      background: #252525;
      border-bottom: 1px solid #333;
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #ff4444;
    }
    .status-dot.connected {
      background: #44ff44;
    }
    main {
      padding: 20px;
      overflow: auto;
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 20px;
    }
    .config-panel {
      grid-column: 1 / -1;
      max-width: 600px;
      margin: 0 auto;
      text-align: center;
    }
    input {
      padding: 10px;
      width: 100%;
      margin-bottom: 10px;
      background: #333;
      border: 1px solid #444;
      color: white;
    }
    button {
      padding: 10px 20px;
      background: #007bff;
      color: white;
      border: none;
      cursor: pointer;
    }
  `;

    connectedCallback() {
        super.connectedCallback();
        wsService.addEventListener('connected', () => this.connected = true);
        wsService.addEventListener('disconnected', () => this.connected = false);
        wsService.addEventListener('message', (e: any) => {
            const msg = e.detail;
            if (msg.type === 'state_update') {
                this.projectState = msg.state;
                this.configMode = false;
            }
        });
    }

    startProject() {
        wsService.send('start_project', { concept: this.concept });
    }

    render() {
        return html`
      <header>
        <h1>LangGraph Scrum Team</h1>
        <div class="status-dot ${this.connected ? 'connected' : ''}" title="${this.connected ? 'Connected' : 'Disconnected'}"></div>
      </header>
      
      <main>
        ${this.configMode ? this.renderConfig() : this.renderDashboard()}
      </main>
    `;
    }

    renderConfig() {
        return html`
      <div class="config-panel">
        <h2>Start New Project</h2>
        <input 
          type="text" 
          .value=${this.concept} 
          @input=${(e: any) => this.concept = e.target.value}
          placeholder="Describe your project concept..."
        >
        <button @click=${this.startProject} ?disabled=${!this.connected}>
          rocket Launch Team
        </button>
      </div>
    `;
    }

    renderDashboard() {
        return html`
      <agent-panel .agents=${this.projectState?.agents || {}}></agent-panel>
      <kanban-board .tickets=${this.projectState?.tickets || []}></kanban-board>
    `;
    }
}
