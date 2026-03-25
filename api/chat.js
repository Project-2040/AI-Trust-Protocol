export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "ERROR: API KEY IS MISSING." });

    try {
        // এই এন্ডপয়েন্টটি বর্তমানে সবচাইতে বেশি কার্যকর
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        // সাকসেস হলে রেসপন্স পাঠাবে
        if (data.candidates && data.candidates.length > 0) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else {
            // এরর হলে তার বিস্তারিত দেখাবে যাতে আমরা বুঝতে পারি কেন হচ্ছে
            const errorInfo = data.error ? `${data.error.message} (${data.error.status})` : "EMPTY_RESPONSE";
            res.status(500).json({ response: "AXIOM DIAGNOSTICS: " + errorInfo });
        }
    } catch (error) {
        res.status(500).json({ response: "SYSTEM CRASH: NETWORK SYNC FAILED." });
    }
}
