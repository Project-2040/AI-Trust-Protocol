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
        // মডেলের নামের আগে সরাসরি /v1beta/ ব্যবহার করে দেখা হচ্ছে
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
            // যদি গুগল কোনো এরর অবজেক্ট পাঠায়, তবে তার পুরো ডিটেইল দেখাবে
            const errorMsg = data.error ? `${data.error.status}: ${data.error.message}` : "NO RESPONSE FROM MODEL";
            res.status(500).json({ response: "DEBUG INFO: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "CORE SYNC FAILED." });
    }
}
