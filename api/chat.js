export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API Key not found in Vercel settings." });
    }

    try {
        // এখানে v1beta এর বদলে v1 ব্যবহার করা হয়েছে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        if (data.candidates && data.candidates[0].content && data.candidates[0].content.parts) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else if (data.error) {
            res.status(500).json({ response: "Google AI Error: " + data.error.message });
        } else {
            res.status(500).json({ response: "AI Core returned an empty response." });
        }
    } catch (error) {
        res.status(500).json({ response: "AI Core Synchronization Failed." });
    }
}
