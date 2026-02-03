import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';

@customElement('team-config')
export class TeamConfig extends LitElement {
  @state() concept = '';
  @state() agents = [
    {
      id: 'product_owner',
      name: 'Product Owner',
      enabled: true,
      required: true,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      role_description: 'Analyze requirements and create user stories.'
    },
    {
      id: 'architect',
      name: 'Solutions Architect',
      enabled: true,
      required: true,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      role_description: 'Design technical architecture and create tickets.'
    },
    {
      id: 'ui_developer',
      name: 'UI Developer',
      enabled: true,
      required: false,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      role_description: 'Implement frontend components and styles.'
    },
    {
      id: 'backend_developer',
      name: 'Backend Developer',
      enabled: true,
      required: false,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      role_description: 'Implement API endpoints and database logic.'
    },
    {
      id: 'tester',
      name: 'QA Tester',
      enabled: true,
      required: false,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.5,
      role_description: 'Verify implemented features and report bugs.'
    },
    {
      id: 'git_agent',
      name: 'Git Manager',
      enabled: true,
      required: true,
      provider: 'openai',
      model: 'gpt-4o',
      temperature: 0.2,
      role_description: 'Manage branches, worktrees and commits.'
    },
    {
      id: 'reviewer',
      name: 'Code Reviewer',
      enabled: true,
      required: false,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.3,
      role_description: 'Review code for best practices and security.'
    }
  ];

  @state() editingAgentId: string | null = null;
  @state() newAgentMode = false;

  static styles = css`
    :host {
      display: block;
      max-width: 900px;
      margin: 0 auto;
      text-align: left;
    }
    h2, h3 { color: white; }
    textarea.concept {
      width: 100%;
      height: 80px;
      padding: 15px;
      background: #333;
      border: 1px solid #444;
      color: white;
      border-radius: 4px;
      font-size: 1rem;
      resize: vertical;
      margin-bottom: 20px;
    }
    .agent-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    .agent-card {
      background: #252525;
      padding: 15px;
      border: 1px solid #444;
      border-radius: 6px;
      transition: all 0.2s;
      position: relative;
    }
    .agent-card.enabled {
      background: #2a3a4a;
      border-color: #007bff;
    }
    .agent-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .role-name { font-weight: bold; cursor: pointer; }
    .status-check {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid #555;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .agent-card.enabled .status-check {
      background: #007bff;
      border-color: #007bff;
    }
    .agent-card.enabled .status-check::after {
      content: "✓";
      color: white;
      font-size: 12px;
    }
    .llm-info {
      font-size: 0.8em;
      color: #aaa;
      margin-top: 5px;
    }
    .actions {
      text-align: center;
      margin-top: 20px;
    }
    button.launch {
      padding: 15px 40px;
      font-size: 1.2rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 30px;
      cursor: pointer;
    }
    button.launch:disabled { background: #444; cursor: not-allowed; }
    
    button.edit-btn {
        background: none;
        border: none;
        color: #888;
        cursor: pointer;
        font-size: 1.2em;
        padding: 0 5px;
    }
    button.edit-btn:hover { color: white; }

    /* Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    .modal {
        background: #252525;
        padding: 25px;
        width: 500px;
        border-radius: 8px;
        border: 1px solid #555;
    }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em; }
    input, select, textarea {
        width: 100%;
        padding: 8px;
        background: #333;
        border: 1px solid #444;
        color: white;
        border-radius: 4px;
        box-sizing: border-box;
    }
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 20px;
    }
    button.save { background: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
    button.cancel { background: #555; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
    button.add-agent {
        background: #444;
        color: #ccc;
        border: 1px dashed #666;
        width: 100%;
        padding: 15px;
        border-radius: 6px;
        cursor: pointer;
    }
    button.add-agent:hover { background: #555; color: white; border-color: white; }
  `;

  toggleAgent(agentId: string) {
    this.agents = this.agents.map(a => {
      if (a.id === agentId && !a.required) {
        return { ...a, enabled: !a.enabled };
      }
      return a;
    });
  }

  editAgent(agentId: string) {
    this.editingAgentId = agentId;
    this.requestUpdate();
  }

  saveAgent(e: Event) {
    e.preventDefault();
    // Logic handled via input bindings on the edited agent object reference in activeAgents list?
    // Actually, simple way is to force update.
    this.editingAgentId = null;
    this.requestUpdate();
  }

  addNewAgent() {
    const newId = `custom_agent_${Date.now()}`;
    this.agents = [...this.agents, {
      id: newId,
      name: 'New Agent',
      enabled: true,
      required: false,
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      role_description: 'describe role...'
    }];
    this.editAgent(newId);
  }

  handleStart() {
    const activeAgents = this.agents.filter(a => a.enabled).map(a => ({
      id: a.id,
      name: a.name,
      // Send full config
      config: {
        provider: a.provider,
        model: a.model,
        temperature: a.temperature,
        role_description: a.role_description
      }
    }));

    this.dispatchEvent(new CustomEvent('start', {
      detail: {
        concept: this.concept,
        agents: activeAgents
      }
    }));
  }

  availableToLaunch() {
    return this.concept.length > 5;
  }

  render() {
    return html`
      <h2>🚀 Start New Project (Advanced)</h2>
      <p style="color: #aaa;">Configure your AI workforce with specific models and roles.</p>
      
      <textarea class="concept"
        .value=${this.concept} 
        @input=${(e: any) => this.concept = e.target.value}
        placeholder="E.g., A personal finance tracker with charts and data export..."
      ></textarea>

      <h3>🤖 Team Composition</h3>
      <div class="agent-grid">
        ${this.agents.map(agent => html`
          <div class="agent-card ${agent.enabled ? 'enabled' : ''}">
            <div class="agent-header">
              <span class="role-name" @click=${() => this.toggleAgent(agent.id)}>${agent.name}</span>
               <div style="display: flex; gap: 10px; align-items: center;">
                 <button class="edit-btn" @click=${() => this.editAgent(agent.id)} title="Configure Agent">⚙️</button>
                 <div class="status-check" @click=${() => this.toggleAgent(agent.id)}></div>
               </div>
            </div>
            
            <div class="llm-info">
              <div>${agent.provider} / ${agent.model}</div>
              <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 4px;">Temp: ${agent.temperature}</div>
            </div>
          </div>
        `)}
        <button class="add-agent" @click=${this.addNewAgent}>+ Add Custom Agent</button>
      </div>

      <div class="actions">
        <button 
          class="launch" 
          @click=${this.handleStart}
          ?disabled=${!this.availableToLaunch()}
        >
          Initialize Team & Start
        </button>
      </div>

      ${this.renderEditModal()}
    `;
  }

  renderEditModal() {
    if (!this.editingAgentId) return '';
    const agent = this.agents.find(a => a.id === this.editingAgentId);
    if (!agent) return '';

    return html`
        <div class="modal-overlay">
            <div class="modal">
                <h3>Configure ${agent.name}</h3>
                
                <div class="form-group">
                    <label>Agent Name</label>
                    <input type="text" .value=${agent.name} @input=${(e: any) => agent.name = e.target.value}>
                </div>

                <div class="form-group">
                    <label>Role / System Prompt</label>
                    <textarea style="height: 80px;" .value=${agent.role_description || ''} @input=${(e: any) => agent.role_description = e.target.value}></textarea>
                </div>

                <div class="form-group" style="display: flex; gap: 10px;">
                    <div style="flex: 1;">
                        <label>Provider</label>
                        <select .value=${agent.provider || 'anthropic'} @change=${(e: any) => { agent.provider = e.target.value; this.requestUpdate(); }}>
                            <option value="anthropic">Anthropic</option>
                            <option value="openai">OpenAI</option>
                            <option value="google">Google Gemini</option>
                        </select>
                    </div>
                    <div style="flex: 1;">
                         <label>Model</label>
                         <input type="text" .value=${agent.model || ''} @input=${(e: any) => agent.model = e.target.value}>
                    </div>
                </div>

                <div class="form-group">
                    <label>Temperature (${agent.temperature})</label>
                    <input type="range" min="0" max="1" step="0.1" .value=${String(agent.temperature)} @input=${(e: any) => { agent.temperature = parseFloat(e.target.value); this.requestUpdate(); }}>
                </div>

                <div class="modal-actions">
                    <button class="cancel" @click=${() => { this.editingAgentId = null; this.requestUpdate(); }}>Close</button>
                </div>
            </div>
        </div>
      `;
  }
}
