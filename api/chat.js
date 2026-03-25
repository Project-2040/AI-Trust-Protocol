export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();
        
        if (data.candidates && data.candidates.length > 0) {
            res.status(200).json({ response: data.candidates[0].content.parts[0].text });
        } else {
            res.status(500).json({ response: "AI Error: " + (data.error ? data.error.message : "No response") });
        }
    } catch (err) {
        res.status(500).json({ response: "Connection Failed" });
    }
}
