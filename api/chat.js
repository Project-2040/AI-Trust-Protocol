export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).send('Denied');
    const { message } = req.body;
    
    // আপনার স্ক্রিনশট থেকে পাওয়া এপিআই কী-র জন্য এই URL সবচাইতে পারফেক্ট
    const apiKey = process.env.GEMINI_API_KEY;
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        if (response.ok && data.candidates) {
            res.status(200).json({ response: data.candidates[0].content.parts[0].text });
        } else {
            // যদি মডেল না পায়, তবে এই মেসেজটি দেখাবে
            const errorReason = data.error ? data.error.message : "MODEL_NOT_READY";
            res.status(500).json({ response: "AXIOM_REJECTED: " + errorReason });
        }
    } catch (err) {
        res.status(500).json({ response: "FATAL: CORE_SYNC_FAILED" });
    }
}
