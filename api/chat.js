export default async function handler(req, res) {
    // শুধুমাত্র POST রিকোয়েস্ট গ্রহণ করবে
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    // API Key না থাকলে এরর দেখাবে
    if (!apiKey) {
        return res.status(500).json({ response: "ERROR: API Key not found in Vercel settings." });
    }

    try {
        // Gemini 1.5 Flash মডেল ব্যবহার করা হচ্ছে
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: message }] }]
            })
        });

        const data = await response.json();

        // ডাটা চেক এবং রেসপন্স পাঠানো
        if (data.candidates && data.candidates[0].content && data.candidates[0].content.parts) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            res.status(200).json({ response: aiResponse });
        } else if (data.error) {
            // যদি গুগল থেকে সরাসরি কোনো এরর আসে
            res.status(500).json({ response: "Google AI Error: " + data.error.message });
        } else {
            res.status(500).json({ response: "AI Core is active but returned an empty response. Check your API Key limits." });
        }
    } catch (error) {
        res.status(500).json({ response: "AI Core Synchronization Failed. Please try again." });
    }
}
