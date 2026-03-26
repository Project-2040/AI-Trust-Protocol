export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "SYSTEM_ERROR: API_KEY_MISSING" });
    }

    try {
        // v1 ভার্সন এবং gemini-pro মডেল ব্যবহার করা হয়েছে
        const url = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${apiKey}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        if (response.ok && data.candidates && data.candidates[0].content) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else {
            const errorDetail = data.error ? data.error.message : "MODEL_UNAVAILABLE";
            res.status(500).json({ response: "CORE_REJECTED: " + errorDetail });
        }
    } catch (err) {
        res.status(500).json({ response: "FATAL_ERROR: SYNC_FAILED" });
    }
}
