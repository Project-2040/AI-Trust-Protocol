export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const { message } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return res.status(500).json({ response: "ERROR: API KEY NOT FOUND." });

    try {
        // একদম বেসিক এবং অফিশিয়াল এন্ডপয়েন্ট
        const response = await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
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
        } else if (data.error) {
            // যদি এরর আসে তবে সেটি ডিটেইলসহ দেখাবে
            res.status(500).json({ response: `AXIOM AI ERROR: ${data.error.message} (${data.error.code})` });
        } else {
            res.status(500).json({ response: "AI CORE returned an empty response." });
        }
    } catch (error) {
        res.status(500).json({ response: "CRITICAL SYNC FAILURE." });
    }
}
