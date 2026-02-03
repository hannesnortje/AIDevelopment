import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { wsService } from './services/websocket';
import './components/kanban-board';
import './components/agent-panel';
import './components/settings-modal';
import './components/team-config';

@customElement('dashboard-app')
export class DashboardApp extends LitElement {
  @state() connected = false;
  @state() projectState: any = null;
  @state() configMode = true;
  @state() showSettings = false;

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
    .header-right {
      display: flex;
      align-items: center;
      gap: 15px;
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
    .icon-btn {
      background: none;
      border: 1px solid #444;
      color: #aaa;
      padding: 5px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9em;
    }
    .icon-btn:hover {
      background: #333;
      color: white;
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
      width: 100%;
      max-width: 900px;
      margin: 0 auto;
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
      } else if (msg.type === 'config_updated') {
        alert("Configuration updated successfully!");
        this.showSettings = false;
      }
    });
  }

  handleStartProject(e: CustomEvent) {
    const { concept, agents } = e.detail;
    wsService.send('start_project', {
      concept,
      agents
    });
  }

  render() {
    return html`
      <header>
        <h1>LangGraph Scrum Team</h1>
        <div class="header-right">
             <button class="icon-btn" @click=${() => this.showSettings = true}>⚙ Settings</button>
            <div class="status-dot ${this.connected ? 'connected' : ''}" title="${this.connected ? 'Connected' : 'Disconnected'}"></div>
        </div>
      </header>
      
      <main>
        ${this.configMode ? this.renderConfig() : this.renderDashboard()}
      </main>

      ${this.showSettings ? html`
        <settings-modal @close=${() => this.showSettings = false}></settings-modal>
      ` : ''}
    `;
  }

  renderConfig() {
    if (!this.connected) {
      return html`
            <div class="config-panel" style="text-align: center; padding: 50px;">
                <h2>Connecting to Server...</h2>
                <div class="status-dot" style="margin: 0 auto;"></div>
            </div>
        `;
    }
    return html`
      <div class="config-panel">
        <team-config @start=${this.handleStartProject}></team-config>
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
