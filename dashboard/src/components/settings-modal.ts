import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { wsService } from '../services/websocket';

@customElement('settings-modal')
export class SettingsModal extends LitElement {
  @state() openaiKey = '';
  @state() anthropicKey = '';
  @state() googleKey = '';
  @state() githubToken = '';

  static styles = css`
    :host {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }
    .modal {
      background: #252525;
      padding: 30px;
      border-radius: 8px;
      width: 500px;
      border: 1px solid #444;
      color: white;
    }
    h2 { margin-top: 0; }
    .form-group {
      margin-bottom: 20px;
      text-align: left;
    }
    label {
      display: block;
      margin-bottom: 5px;
      color: #aaa;
    }
    input {
      width: 100%;
      padding: 10px;
      box-sizing: border-box;
      background: #333;
      border: 1px solid #444;
      color: white;
      border-radius: 4px;
    }
    .actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    button {
      padding: 10px 20px;
      cursor: pointer;
      border-radius: 4px;
      border: none;
    }
    button.save {
      background: #007bff;
      color: white;
    }
    button.cancel {
      background: #555;
      color: white;
    }
  `;

  save() {
    wsService.send('update_config', {
      config: {
        OPENAI_API_KEY: this.openaiKey,
        ANTHROPIC_API_KEY: this.anthropicKey,
        GOOGLE_API_KEY: this.googleKey,
        GITHUB_TOKEN: this.githubToken
      }
    });
    this.close();
  }

  close() {
    this.dispatchEvent(new CustomEvent('close'));
  }

  render() {
    return html`
      <div class="modal">
        <h2>Settings & API Keys</h2>
        <p style="color: #888; font-size: 0.9em; margin-bottom: 20px;">
          Configuration is updated in the running server. To persist changes, use the .env file.
        </p>

        <div class="form-group">
          <label>OpenAI API Key</label>
          <input 
            type="password" 
            .value=${this.openaiKey} 
            @input=${(e: any) => this.openaiKey = e.target.value}
            placeholder="sk-..."
          >
        </div>


        <div class="form-group">
          <label>Anthropic API Key</label>
          <input 
            type="password" 
            .value=${this.anthropicKey} 
            @input=${(e: any) => this.anthropicKey = e.target.value}
            placeholder="sk-ant-..."
          >
        </div>

        <div class="form-group">
          <label>Google API Key</label>
          <input 
            type="password" 
            .value=${this.googleKey} 
            @input=${(e: any) => this.googleKey = e.target.value}
            placeholder="AIza..."
          >
        </div>

        <div class="form-group">
          <label>GitHub Token</label>
          <input 
            type="password" 
            .value=${this.githubToken} 
            @input=${(e: any) => this.githubToken = e.target.value}
            placeholder="ghp_..."
          >
        </div>

        <div class="actions">
          <button class="cancel" @click=${this.close}>Cancel</button>
          <button class="save" @click=${this.save}>Save Configuration</button>
        </div>
      </div>
    `;
  }
}
