// Small line icons for the Edukasaun login screen, drawn so they look the
// same on every computer (no icon theme or symbol font is needed).
import QtQuick 2.15

Canvas {
    id: icon
    property string name: ""
    property color ink: "white"
    width: 20; height: 20
    onInkChanged: requestPaint()
    onNameChanged: requestPaint()
    onWidthChanged: requestPaint()

    onPaint: {
        var c = getContext("2d"); c.reset()
        var w = width, h = height, cx = w / 2, cy = h / 2
        c.strokeStyle = ink; c.fillStyle = ink
        c.lineWidth = Math.max(1.5, w * 0.09); c.lineCap = "round"; c.lineJoin = "round"
        c.beginPath()
        if (name === "power") {
            var r = w * 0.36
            c.arc(cx, cy + h * 0.04, r, -Math.PI / 2 + 0.7, 3 * Math.PI / 2 - 0.7, false)
            c.moveTo(cx, h * 0.1); c.lineTo(cx, cy)
            c.stroke()
        } else if (name === "restart") {
            var rr = w * 0.34
            c.arc(cx, cy, rr, -Math.PI / 2, Math.PI * 1.2, false); c.stroke()
            c.beginPath(); c.moveTo(cx - w * 0.02, cy - rr - h * 0.13); c.lineTo(cx + w * 0.17, cy - rr); c.lineTo(cx - w * 0.02, cy - rr + h * 0.13)
            c.closePath(); c.fill()
        } else if (name === "suspend") {
            // crescent moon
            c.arc(cx, cy, w * 0.36, 0, Math.PI * 2, false); c.fill()
            c.globalCompositeOperation = "destination-out"
            c.beginPath(); c.arc(cx + w * 0.17, cy - h * 0.14, w * 0.3, 0, Math.PI * 2, false); c.fill()
            c.globalCompositeOperation = "source-over"
        } else if (name === "hibernate") {
            c.moveTo(w * 0.25, h * 0.2); c.lineTo(w * 0.75, h * 0.2); c.lineTo(w * 0.25, h * 0.8); c.lineTo(w * 0.75, h * 0.8)
            c.stroke()
        } else if (name === "globe") {
            var g = w * 0.38
            c.arc(cx, cy, g, 0, Math.PI * 2, false)
            c.moveTo(cx - g, cy); c.lineTo(cx + g, cy)
            c.stroke()
            c.beginPath(); c.ellipse(cx - g * 0.45, cy - g, g * 0.9, g * 2); c.stroke()
        } else if (name === "keyboard") {
            c.lineWidth = Math.max(1.2, w * 0.07)
            var kx = w * 0.08, ky = h * 0.24, kw = w * 0.84, kh = h * 0.52, kr = w * 0.08
            c.moveTo(kx + kr, ky); c.lineTo(kx + kw - kr, ky); c.quadraticCurveTo(kx + kw, ky, kx + kw, ky + kr)
            c.lineTo(kx + kw, ky + kh - kr); c.quadraticCurveTo(kx + kw, ky + kh, kx + kw - kr, ky + kh)
            c.lineTo(kx + kr, ky + kh); c.quadraticCurveTo(kx, ky + kh, kx, ky + kh - kr)
            c.lineTo(kx, ky + kr); c.quadraticCurveTo(kx, ky, kx + kr, ky)
            c.stroke()
            var d = w * 0.075
            for (var i = 0; i < 4; i++) { c.fillRect(w * (0.2 + i * 0.18) - d / 2, h * 0.38 - d / 2, d, d) }
            c.beginPath(); c.moveTo(w * 0.3, h * 0.6); c.lineTo(w * 0.7, h * 0.6); c.stroke()
        } else if (name === "access") {
            // person in a circle (universal access)
            c.lineWidth = Math.max(1.2, w * 0.07)
            c.arc(cx, cy, w * 0.42, 0, Math.PI * 2, false); c.stroke()
            c.beginPath(); c.arc(cx, h * 0.27, w * 0.075, 0, Math.PI * 2, false); c.fill()
            c.beginPath()
            c.moveTo(w * 0.28, h * 0.4); c.lineTo(w * 0.72, h * 0.4)
            c.moveTo(cx, h * 0.4); c.lineTo(cx, h * 0.58)
            c.lineTo(w * 0.38, h * 0.76); c.moveTo(cx, h * 0.58); c.lineTo(w * 0.62, h * 0.76)
            c.stroke()
        } else if (name === "session") {
            c.lineWidth = Math.max(1.2, w * 0.07)
            c.rect(w * 0.12, h * 0.18, w * 0.76, h * 0.5); c.stroke()
            c.beginPath(); c.moveTo(w * 0.35, h * 0.84); c.lineTo(w * 0.65, h * 0.84)
            c.moveTo(cx, h * 0.68); c.lineTo(cx, h * 0.84); c.stroke()
        } else if (name === "arrow") {
            c.moveTo(w * 0.18, cy); c.lineTo(w * 0.82, cy)
            c.moveTo(w * 0.55, h * 0.22); c.lineTo(w * 0.82, cy); c.lineTo(w * 0.55, h * 0.78)
            c.stroke()
        } else if (name === "back") {
            c.moveTo(w * 0.62, h * 0.2); c.lineTo(w * 0.32, cy); c.lineTo(w * 0.62, h * 0.8)
            c.stroke()
        } else if (name === "check") {
            c.moveTo(w * 0.2, h * 0.52); c.lineTo(w * 0.42, h * 0.74); c.lineTo(w * 0.8, h * 0.28)
            c.stroke()
        } else if (name === "user") {
            c.arc(cx, h * 0.36, w * 0.18, 0, Math.PI * 2, false); c.fill()
            c.beginPath(); c.arc(cx, h * 0.98, w * 0.36, Math.PI, 0, false); c.fill()
        } else if (name === "plus") {
            c.moveTo(cx, h * 0.22); c.lineTo(cx, h * 0.78); c.moveTo(w * 0.22, cy); c.lineTo(w * 0.78, cy)
            c.stroke()
        }
    }
}
