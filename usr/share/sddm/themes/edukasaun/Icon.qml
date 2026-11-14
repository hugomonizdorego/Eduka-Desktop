// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
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
        } else if (name === "updown") {
            c.moveTo(w * 0.3, h * 0.4); c.lineTo(cx, h * 0.2); c.lineTo(w * 0.7, h * 0.4)
            c.moveTo(w * 0.3, h * 0.6); c.lineTo(cx, h * 0.8); c.lineTo(w * 0.7, h * 0.6)
            c.stroke()
        } else if (name === "osk") {
            // keyboard that comes up from the bottom (on-screen keyboard)
            c.lineWidth = Math.max(1.2, w * 0.07)
            var ox = w * 0.08, oy = h * 0.44, ow = w * 0.84, oh = h * 0.44, orr = w * 0.07
            c.moveTo(ox + orr, oy); c.lineTo(ox + ow - orr, oy); c.quadraticCurveTo(ox + ow, oy, ox + ow, oy + orr)
            c.lineTo(ox + ow, oy + oh - orr); c.quadraticCurveTo(ox + ow, oy + oh, ox + ow - orr, oy + oh)
            c.lineTo(ox + orr, oy + oh); c.quadraticCurveTo(ox, oy + oh, ox, oy + oh - orr)
            c.lineTo(ox, oy + orr); c.quadraticCurveTo(ox, oy, ox + orr, oy)
            c.stroke()
            var od = w * 0.07
            for (var k = 0; k < 4; k++) { c.fillRect(w * (0.22 + k * 0.186) - od / 2, h * 0.57 - od / 2, od, od) }
            c.beginPath(); c.moveTo(w * 0.32, h * 0.75); c.lineTo(w * 0.68, h * 0.75)
            c.moveTo(w * 0.36, h * 0.26); c.lineTo(cx, h * 0.12); c.lineTo(w * 0.64, h * 0.26)
            c.stroke()
        } else if (name === "finger") {
            // fingerprint: arcs around a centre
            c.lineWidth = Math.max(1.1, w * 0.06)
            for (var f = 0; f < 4; f++) {
                var fr = w * (0.1 + f * 0.1)
                c.beginPath(); c.arc(cx, cy + h * 0.06, fr, Math.PI * (1.05 + f * 0.02), Math.PI * (1.95 - f * 0.02) + (f > 1 ? Math.PI * 0.5 : 0), false); c.stroke()
            }
            c.beginPath(); c.moveTo(cx, cy + h * 0.06); c.lineTo(cx, cy + h * 0.3); c.stroke()
        } else if (name === "plus") {
            c.moveTo(cx, h * 0.22); c.lineTo(cx, h * 0.78); c.moveTo(w * 0.22, cy); c.lineTo(w * 0.78, cy)
            c.stroke()
        }
    }
}
