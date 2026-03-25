export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API KEY IS MISSING IN VERCEL." });
    }

    try {
        // এই নির্দিষ্ট URL-টি কোনোভাবেই ফেইল করবে না
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: message }]
                }]
            })
        });

        const data = await response.json();

        if (data.candidates && data.candidates.length > 0) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else {
            // যদি গুগল এরর দেয় তবে সেটি এখানে দেখাবে
            const errorMsg = data.error ? data.error.message : "AI CORE BUSY. RETRY.";
            res.status(500).json({ response: "SYSTEM: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "CONNECTION LOST. PLEASE RETRY." });
    }
}
