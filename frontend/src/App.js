import React, { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [results, setResults] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please upload an Excel file.");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sender_email", email);
    formData.append("app_password", password);
    formData.append("subject", subject);
    formData.append("body", body);

    try {
      const res = await axios.post("http://localhost:8000/send-emails/", formData);
      console.log("Email API Response:", res.data);
      setResults(res.data.results);
    } catch (err) {
      console.error("Sending failed:", err.response?.data || err.message);
      alert("Error sending emails: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-50 to-purple-100 p-6">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-2xl">
        <h1 className="text-3xl font-bold text-blue-700 text-center mb-6">📬 Bulk Gmail Mailer</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium text-gray-700">Gmail Address</label>
            <input type="email" className="w-full border p-2 rounded" onChange={e => setEmail(e.target.value)} required />
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700">App Password</label>
            <input type="password" className="w-full border p-2 rounded" onChange={e => setPassword(e.target.value)} required />
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700">Subject</label>
            <input type="text" className="w-full border p-2 rounded" onChange={e => setSubject(e.target.value)} required />
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700">Email Body</label>
            <textarea rows="4" className="w-full border p-2 rounded" onChange={e => setBody(e.target.value)} required />
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700">Upload Excel (.xlsx)</label>
            <input type="file" accept=".xlsx" className="w-full" onChange={e => setFile(e.target.files[0])} />
          </div>

          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white w-full py-2 rounded mt-4 font-semibold">
            🚀 Send Emails
          </button>
        </form>

        {results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">📊 Results</h2>
            <ul className="space-y-1">
              {results.map((r, i) => (
                <li key={i} className={`text-sm ${r.status === "Sent" ? "text-green-600" : "text-red-600"}`}>
                  {r.email} — {r.status}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
