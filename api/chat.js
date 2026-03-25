export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "ERROR: API KEY NOT FOUND." });

    // আমরা এই মডেলটি দিয়ে চেষ্টা করব
    const model = "gemini-1.5-flash-latest"; 

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
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
            // যদি flash-latest কাজ না করে, তবে সরাসরি মেসেজ দেখাবে
            const errorMsg = data.error ? data.error.message : "AI Core connection reset. Please retry.";
            res.status(500).json({ response: "SYSTEM: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "CORE OFFLINE." });
    }
}
