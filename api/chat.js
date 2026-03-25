export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "SYSTEM: API KEY NOT CONFIGURED." });

    try {
        // একদম ডাইরেক্ট এন্ডপয়েন্ট এবং মডেল পাথ
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
            // বিস্তারিত এরর মেসেজ যাতে আমরা বুঝতে পারি সমস্যা কোথায়
            const errorMsg = data.error ? `${data.error.message} (Code: ${data.error.code})` : "NO RESPONSE";
            res.status(500).json({ response: "AXIOM CORE ERROR: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "NETWORK SYNC FAILED." });
    }
}
