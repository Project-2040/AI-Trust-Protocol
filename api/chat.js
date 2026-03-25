export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "DEBUG: API_KEY_MISSING_IN_VERCEL" });

    try {
        // আমরা এখন সবচাইতে সরাসরি এবং সহজ এন্ডপয়েন্ট ব্যবহার করব
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents: [{ parts: [{ text: message }] }] })
        });

        const data = await response.json();

        // যদি সাকসেস হয়
        if (response.ok && data.candidates) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            return res.status(200).json({ response: aiResponse });
        } 

        // যদি এরর হয়, তবে গুগলের পাঠানো আসল মেসেজটি স্ক্রিনে দেখাবে
        const detailedError = data.error 
            ? `Code: ${data.error.code} | Status: ${data.error.status} | Msg: ${data.error.message}`
            : JSON.stringify(data);

        res.status(500).json({ response: `DIAGNOSTIC_LOG: ${detailedError}` });

    } catch (error) {
        res.status(500).json({ response: `CRITICAL_EXCEPTION: ${error.message}` });
    }
}
