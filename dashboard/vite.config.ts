import { defineConfig } from 'vite'

export default defineConfig({
    build: {
        outDir: '../langgraph_scrum/static',
        emptyOutDir: true,
    },
    server: {
        port: 3000,
        proxy: {
            '/ws': {
                target: 'ws://localhost:8765',
                ws: true
            }
        }
    }
})
