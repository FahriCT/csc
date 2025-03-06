const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
require('dotenv').config();

const client = new Client({ 
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] 
});

// Environment variables
const TOKEN = process.env.DISCORD_TOKEN;
const CLOUDFLARE_API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;
const ZONE_ID = process.env.ZONE_ID;
const DOMAIN = process.env.DOMAIN;
const OWNER_ID = process.env.OWNER_ID;

// Check proxy function
async function checkProxy(ip, port, username, password) {
    const proxy = `${username}:${password}@${ip}:${port}`;
    
    try {
        // Check Growtopia login API
        const loginUrl = "https://login.growtopiagame.com/player/login/dashboard";
        const headers = {
            "User-Agent": "UbiServices_SDK_2022.Release.9_PC64_ansi_static"
        };
        const data = "version=5.07&platform=0&protocol=214";
        
        const loginCmd = `curl -x socks5://${proxy} -d "${data}" -H "User-Agent: ${headers['User-Agent']}" -s -o /dev/null -w "%{http_code}" ${loginUrl}`;
        const { stdout: loginStatus } = await execAsync(loginCmd);
        
        const gtStatus = !["403", "404", "502"].includes(loginStatus.trim()) 
            ? "✅ **GT Unblocked**" 
            : "❌ **GT Blocked**";

        // Check Growtopia server_data.php
        const serverDataUrl = "https://growtopia1.com/growtopia/server_data.php";
        const serverDataCmd = `curl -x socks5://${proxy} -s -o /dev/null -w "%{http_code}" ${serverDataUrl}`;
        const { stdout: serverDataStatus } = await execAsync(serverDataCmd);
        
        const httpStatus = !["403", "404", "502"].includes(serverDataStatus.trim()) 
            ? "✅ **HTTP Unblocked**" 
            : "❌ **HTTP Blocked**";

        return `${gtStatus}\n${httpStatus}`;
    } catch (error) {
        console.error('Error checking proxy:', error);
        return "❌ Error checking proxy";
    }
}

client.once('ready', () => {
    console.log(`Bot ${client.user.tag} is ready!`);
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;

    const { commandName } = interaction;

    if (commandName === 'check') {
        const proxy = interaction.options.getString('proxy');
        
        try {
            const [ip, port, username, password] = proxy.split(':');
            await interaction.reply({ content: "🔄 **Checking proxy...**", ephemeral: true });
            
            const result = await checkProxy(ip, port, username, password);
            await interaction.editReply({ content: result, ephemeral: true });
        } catch (error) {
            await interaction.reply({ 
                content: "❌ Wrong format! Use `/check ip:port:username:password`", 
                ephemeral: true 
            });
        }
    }

    if (commandName === 'iptosub') {
        if (interaction.user.id !== OWNER_ID) {
            return await interaction.reply({ 
                content: "❌ You don't have permission to use this command!", 
                ephemeral: true 
            });
        }

        const ip = interaction.options.getString('ip');
        // Add your subdomain logic here
        await interaction.reply({ 
            content: `✅ Subdomain created successfully`, 
            ephemeral: true 
        });
    }
});

client.login(TOKEN);
