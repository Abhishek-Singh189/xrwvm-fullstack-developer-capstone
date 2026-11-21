import React, { useState } from "react";
import "./Register.css";
import Header from "../Header/Header";

export default function Register() {
  const [form, setForm] = useState({
    username: "", firstName: "", lastName: "", email: "", password: ""
  });

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("/djangoapp/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userName: form.username,
          firstName: form.firstName,
          lastName: form.lastName,
          email: form.email,
          password: form.password
        })
      });
      const data = await response.json();
      if (response.ok) {
        alert("Registration successful. Please log in.");
        window.location.href = "/login";
      } else {
        alert(data.error || "Registration failed");
      }
    } catch (error) {
      alert("Could not connect to the server");
    }
  };

  return (
    <div>
      <Header />
      <div className="register_container">
        <h2 className="header">Create Account</h2>
        <form onSubmit={submit}>
          <div className="input_field"><input className="input" name="username" placeholder="Username" value={form.username} onChange={update} required /></div>
          <div className="input_field"><input className="input" name="firstName" placeholder="First Name" value={form.firstName} onChange={update} required /></div>
          <div className="input_field"><input className="input" name="lastName" placeholder="Last Name" value={form.lastName} onChange={update} required /></div>
          <div className="input_field"><input className="input" type="email" name="email" placeholder="Email" value={form.email} onChange={update} required /></div>
          <div className="input_field"><input className="input" type="password" name="password" placeholder="Password" value={form.password} onChange={update} required /></div>
          <div className="submit_panel"><button className="submit" type="submit">Register</button></div>
        </form>
      </div>
    </div>
  );
}
