
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
      setResults(res.data.results);
    } catch (err) {
      alert("Error sending emails: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 flex items-center justify-center px-4 py-8">
      <div className="max-w-3xl w-full bg-white shadow-2xl rounded-2xl p-10">
        <h1 className="text-4xl font-extrabold text-center text-indigo-700 mb-8">📬 Gmail Bulk Mailer</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Gmail Address</label>
            <input type="email" required className="mt-1 w-full border border-gray-300 p-2 rounded-md shadow-sm" onChange={e => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">App Password</label>
            <input type="password" required className="mt-1 w-full border border-gray-300 p-2 rounded-md shadow-sm" onChange={e => setPassword(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Subject</label>
            <input type="text" required className="mt-1 w-full border border-gray-300 p-2 rounded-md shadow-sm" onChange={e => setSubject(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email Body</label>
            <textarea rows="4" required className="mt-1 w-full border border-gray-300 p-2 rounded-md shadow-sm" onChange={e => setBody(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Excel File (.xlsx)</label>
            <input type="file" accept=".xlsx" required className="mt-1 w-full" onChange={e => setFile(e.target.files[0])} />
          </div>
          <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 font-semibold">🚀 Send Emails</button>
        </form>

        {results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-800 mb-2">📊 Send Status</h2>
            <ul className="text-sm space-y-1 max-h-60 overflow-y-auto border rounded p-3 bg-gray-50">
              {results.map((r, i) => (
                <li key={i} className={r.status === "Sent" ? "text-green-600" : "text-red-600"}>
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
