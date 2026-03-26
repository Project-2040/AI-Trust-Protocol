export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    try {
        // মডেলের নাম একদম সহজভাবে রাখা হয়েছে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
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
            // যদি মডেল খুঁজে না পায়, তবে সেটির বিস্তারিত এরর দেখাবে
            const errorMsg = data.error ? data.error.message : "Model mismatch or Access denied";
            res.status(500).json({ response: `SYSTEM_HALT: ${errorMsg}` });
        }
    } catch (err) {
        res.status(500).json({ response: "CRITICAL_FAILURE: SYNC_ERROR" });
    }
}
