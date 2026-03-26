export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    try {
        // এই URL-টি সরাসরি লেটেস্ট মডেলকে টার্গেট করবে যা সবার জন্য কাজ করে
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`;

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
            // যদি মডেল না পায়, তবে সিস্টেমের আসল এরর মেসেজ পাঠাবে
            const errorMsg = data.error ? data.error.message : "REACHED_LIMIT_OR_UNSUPPORTED_REGION";
            res.status(500).json({ response: "AI_CORE_ERROR: " + errorMsg });
        }
    } catch (err) {
        res.status(500).json({ response: "CONNECTION_FAILED_TO_CORE" });
    }
}
