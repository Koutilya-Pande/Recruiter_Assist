import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../App";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      const result = await login(email, password);
      if (result.success) {
        navigate("/dashboard");
      } else {
        setError(result.error || "Invalid credentials or server error.");
      }
    } catch (err) {
      setError(err.message || "Invalid credentials or server error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Left Side */}
      <div style={{ 
        flex: 1, 
        background: "#101728", 
        color: "#fff", 
        display: "flex", 
        flexDirection: "column", 
        justifyContent: "center", 
        alignItems: "center", 
        padding: 48 
      }}>
        <div style={{ 
          display: "flex", 
          flexDirection: "column", 
          alignItems: "center", 
          justifyContent: "center", 
          width: "100%" 
        }}>
          <div style={{ 
            fontSize: 48, 
            fontWeight: 700, 
            marginBottom: 16,
            color: "#3b82f6"
          }}>
            👥
          </div>
          <span style={{ 
            fontSize: 32, 
            fontWeight: 700, 
            letterSpacing: 1, 
            textAlign: "center",
            marginBottom: 16
          }}>
            Recruiter Assist
          </span>
          <span style={{ 
            fontSize: 18, 
            textAlign: "center", 
            color: "#9ca3af",
            lineHeight: 1.6
          }}>
            AI-powered recruiting platform with resume parsing and job-candidate matching
          </span>
        </div>
      </div>
      
      {/* Right Side */}
      <div style={{ 
        flex: 1, 
        background: "#f7f9fb", 
        display: "flex", 
        flexDirection: "column", 
        justifyContent: "center", 
        alignItems: "center", 
        position: "relative" 
      }}>
        <form onSubmit={handleSubmit} style={{ 
          width: 340, 
          background: "#fff", 
          borderRadius: 12, 
          boxShadow: "0 2px 16px rgba(0,0,0,0.06)", 
          padding: 40, 
          display: "flex", 
          flexDirection: "column", 
          alignItems: "stretch" 
        }}>
          <h2 style={{ 
            fontWeight: 700, 
            fontSize: 32, 
            marginBottom: 24, 
            textAlign: "center", 
            color: "#101728" 
          }}>
            Welcome Back
          </h2>
          
          <label style={{ fontWeight: 500, marginBottom: 6, color: "#374151" }}>
            Email
          </label>
          <input 
            type="email" 
            value={email} 
            onChange={e => setEmail(e.target.value)} 
            placeholder="you@example.com" 
            required 
            style={{ 
              marginBottom: 18, 
              padding: 12, 
              borderRadius: 6, 
              border: "1px solid #d1d5db", 
              fontSize: 16,
              outline: "none",
              transition: "border-color 0.2s"
            }}
            onFocus={(e) => e.target.style.borderColor = "#3b82f6"}
            onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
          />
          
          <label style={{ fontWeight: 500, marginBottom: 6, color: "#374151" }}>
            Password
          </label>
          <input 
            type="password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
            style={{ 
              marginBottom: 18, 
              padding: 12, 
              borderRadius: 6, 
              border: "1px solid #d1d5db", 
              fontSize: 16,
              outline: "none",
              transition: "border-color 0.2s"
            }}
            onFocus={(e) => e.target.style.borderColor = "#3b82f6"}
            onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
          />
          
          {error && (
            <div style={{ 
              color: "#d32f2f", 
              marginBottom: 12, 
              textAlign: "center",
              fontSize: 14,
              padding: 8,
              backgroundColor: "#fef2f2",
              borderRadius: 4
            }}>
              {error}
            </div>
          )}
          
          <button 
            type="submit" 
            disabled={isLoading}
            style={{ 
              background: "#101728", 
              color: "#fff", 
              border: "none", 
              borderRadius: 6, 
              padding: 12, 
              fontWeight: 600, 
              fontSize: 18, 
              marginBottom: 8, 
              cursor: isLoading ? "not-allowed" : "pointer",
              opacity: isLoading ? 0.7 : 1,
              transition: "opacity 0.2s"
            }}
          >
            {isLoading ? "Signing in..." : "Log In"}
          </button>
          
          <div style={{ textAlign: "center", color: "#6b7280", fontSize: 15 }}>
            Don't have an account?{" "}
            <span style={{ color: "#3b82f6", cursor: "pointer" }}>
              Sign up
            </span>
          </div>
          
          <div style={{ 
            position: "absolute", 
            right: 32, 
            bottom: 32, 
            textAlign: "right",
            fontSize: 15,
            color: "#6b7280"
          }}>
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontWeight: 600, color: "#101728" }}>Recruiter Assist</span>
            </div>
            <div>info@recruiterassist.com</div>
            <div>123-456-7890</div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage; 