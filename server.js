const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const { findAnswer } = require('./knowledge');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const frontendPath = path.join(__dirname, '../frontend');
app.use(express.static(frontendPath));

app.get('/api/test', (req, res) => {
    res.json({ message: 'Server OK' });
});

app.post('/api/chat', async (req, res) => {
    try {
        const userMessage = req.body.message;
        
        console.log('\n' + '='.repeat(60));
        console.log('USER:', userMessage);
        
        if (!userMessage) {
            return res.status(400).json({ error: 'Pesan kosong' });
        }

        // STEP 1: PRIORITAS KNOWLEDGE BASE
        console.log('🔍 Searching Knowledge Base...');
        const kbAnswer = findAnswer(userMessage);
        
        if (kbAnswer) {
            console.log('✅ FOUND IN KB - USING KNOWLEDGE BASE');
            console.log('='.repeat(60) + '\n');
            return res.json({ reply: kbAnswer, source: 'kb' });
        }

        // STEP 2: Jika tidak ada, gunakan Ollama
        console.log('⚠️  NOT IN KB - USING OLLAMA');
        
        const response = await axios.post('http://localhost:11434/api/generate', {
            model: 'llama3',
            prompt: userMessage,
            stream: false,
        }, { timeout: 180000 });

        const reply = response.data.response.trim();
        console.log('✅ Ollama response received');
        console.log('='.repeat(60) + '\n');
        
        return res.json({ reply: reply, source: 'ollama' });

    } catch (error) {
        console.error('❌ ERROR:', error.message);
        console.log('='.repeat(60) + '\n');
        return res.status(500).json({ error: 'Error: ' + error.message });
    }
});

app.listen(PORT, () => {
    console.log('\n🚀 SARA_BOT SERVER STARTED\n');
});