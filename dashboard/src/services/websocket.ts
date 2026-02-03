export class WebSocketService extends EventTarget {
    private ws: WebSocket | null = null;
    private url: string;
    private reconnectInterval = 3000;

    constructor(url: string = `ws://${location.host}/ws`) {
        super();
        this.url = url;
        this.connect();
    }

    private connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket Connected');
            this.dispatchEvent(new Event('connected'));
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.dispatchEvent(new CustomEvent('message', { detail: message }));
            } catch (e) {
                console.error('Failed to parse message', event.data);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket Disconnected, reconnecting...');
            this.dispatchEvent(new Event('disconnected'));
            setTimeout(() => this.connect(), this.reconnectInterval);
        };
    }

    send(type: string, payload: any = {}) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, ...payload }));
        } else {
            console.warn('WebSocket not connected');
        }
    }
}

export const wsService = new WebSocketService();
