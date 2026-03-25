export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "AXIOM: API KEY MISSING." });

    try {
        // মডেল হিসেবে আমরা gemini-1.5-flash ব্যবহার করছি যা ফ্রি এবং স্ট্যাবল
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        if (data.candidates && data.candidates.length > 0) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else {
            // যদি গুগল থেকে কোনো এরর আসে সেটি স্পষ্টভাবে দেখাবে
            const errorInfo = data.error ? `${data.error.message} (${data.error.status})` : "EMPTY_RESPONSE";
            res.status(500).json({ response: "AXIOM SYSTEM: " + errorInfo });
        }
    } catch (error) {
        res.status(500).json({ response: "CRITICAL CORE DISCONNECT." });
    }
}
