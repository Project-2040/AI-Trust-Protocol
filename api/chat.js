export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API KEY MISSING." });
    }

    try {
        // সবচাইতে স্ট্যাবল মডেল gemini-pro ব্যবহার করা হয়েছে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        if (data.candidates && data.candidates[0].content) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else {
            const errorDetail = data.error ? data.error.message : "AI CORE SYNC ERROR";
            res.status(500).json({ response: "SYSTEM: " + errorDetail });
        }
    } catch (error) {
        res.status(500).json({ response: "CONNECTION FAILED." });
    }
}
