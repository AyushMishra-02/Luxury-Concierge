import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    
    // Hardcoded Render URL so you never have to worry about environment variables
    const renderUrl = "https://luxury-concierge.onrender.com/api/plan-trip";
    
    console.log("Proxying request to:", renderUrl);
    
    const backendRes = await fetch(renderUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    
    if (!backendRes.ok) {
      const errorText = await backendRes.text();
      console.error("Backend error:", errorText);
      return NextResponse.json({ error: errorText }, { status: backendRes.status });
    }
    
    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Proxy error:", error.message);
    return NextResponse.json({ error: error.message || "Failed to proxy request" }, { status: 500 });
  }
}
