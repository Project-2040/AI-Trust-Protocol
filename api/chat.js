export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API KEY NOT FOUND." });
    }

    try {
        // মডেল হিসেবে gemini-1.5-flash এবং v1beta এন্ডপয়েন্ট ব্যবহার করা হয়েছে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
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
            // বিস্তারিত এরর মেসেজ দেখাবে যাতে আপনি বুঝতে পারেন সমস্যা কোথায়
            const errorMsg = data.error ? data.error.message : "AI CORE IS SYNCING, PLEASE RETRY.";
            res.status(500).json({ response: "SYSTEM: " + errorMsg });
        }
    } catch (error) {
        res.status(500).json({ response: "CORE SYNCHRONIZATION FAILED." });
    }
}
