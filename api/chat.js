export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API KEY NOT FOUND IN VERCEL." });
    }

    try {
        // এই URL টি এখন সরাসরি v1beta এবং gemini-1.5-flash-latest ব্যবহার করবে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`, {
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
            // যদি গুগল কোনো এরর দেয় তবে সেটি এখানে দেখাবে
            const errorMsg = data.error ? data.error.message : "MODEL NOT READY";
            res.status(500).json({ response: "GOOGLE AI ERROR: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "CONNECTION FAILED. PLEASE RETRY." });
    }
}
