import React, { useState } from "react";
import axios from "axios";

function App() {
  const [senderEmail, setSenderEmail] = useState("");
  const [appPassword, setAppPassword] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setStatus("Please upload an Excel file (.xlsx)");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sender_email", senderEmail);
    formData.append("app_password", appPassword);
    formData.append("subject", subject);
    formData.append("body", body);

    try {
      const response = await axios.post(
        "https://bulk-mail-backend-amrc.onrender.com/send-emails/",
        formData
      );
      setStatus(response.data.message || response.data.error);
    } catch (error) {
      setStatus("Failed to send emails. Please check the logs or try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-white flex items-center justify-center p-6">
      <div className="w-full max-w-2xl bg-white shadow-xl rounded-2xl p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center text-blue-600">📧 Bulk Mail Sender</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Your Gmail"
            value={senderEmail}
            onChange={(e) => setSenderEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="App Password (Gmail)"
            value={appPassword}
            onChange={(e) => setAppPassword(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Email Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Email Body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            required
            rows="5"
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
          <input
            type="file"
            accept=".xlsx"
            onChange={(e) => setFile(e.target.files[0])}
            required
            className="w-full px-4 py-2 border rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition"
          >
            Send Emails
          </button>
        </form>
        {status && <p className="text-center text-sm text-gray-700">{status}</p>}
      </div>
    </div>
  );
}

export default App;
