// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Round picture of a user (0.11 RC3): the face picture of the account, or,
// for SDDM's grey default face, the first letter of the name on a color of
// the Eduka palette (the same name always gets the same color).
import QtQuick 2.15

Item {
    id: avatar
    property var theme
    property string source: ""
    property string name: ""
    property real ring: 3
    property color ringColor: theme.accent
    readonly property var colors: ["#3fa684", "#2f8fd8", "#7c6cf0", "#159a9c", "#f08c2e", "#e5484d", "#d6619e"]
    readonly property bool generic: source.length === 0 || /\/sddm\/faces\/\.face\.icon$/.test(source)
    readonly property color face: {
        var h = 0
        for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 9973
        return colors[h % colors.length]
    }

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        color: avatar.theme.contrast ? "#000000" : "#ffffff"
        border.color: avatar.ringColor; border.width: avatar.ring
    }
    Rectangle {
        id: disc
        anchors.fill: parent
        anchors.margins: avatar.ring + Math.max(1, avatar.width * 0.03)
        radius: width / 2
        visible: avatar.generic || picture.status !== Image.Ready
        color: avatar.theme.contrast ? "#000000" : avatar.face
        Text {
            anchors.centerIn: parent
            visible: avatar.name.length > 0
            text: avatar.name.charAt(0).toUpperCase()
            color: "white"; font.pixelSize: parent.width * 0.46; font.bold: true
        }
        Icon {
            anchors.centerIn: parent
            visible: avatar.name.length === 0
            width: parent.width * 0.6; height: width
            name: "user"; ink: "white"
        }
    }
    Image {
        id: picture
        anchors.fill: disc
        source: avatar.generic ? "" : avatar.source
        sourceSize.width: Math.ceil(disc.width * 2); sourceSize.height: Math.ceil(disc.height * 2)
        fillMode: Image.PreserveAspectCrop
        visible: false
        asynchronous: true
    }
    // Round picture: drawn through a canvas clip (no graphical effects module needed).
    Canvas {
        id: round
        anchors.fill: disc
        property string url: picture.status === Image.Ready ? String(picture.source) : ""
        visible: url.length > 0
        onUrlChanged: if (url.length > 0) { if (isImageLoaded(url)) requestPaint(); else loadImage(url) }
        onImageLoaded: requestPaint()
        onWidthChanged: requestPaint()
        onPaint: {
            var c = getContext("2d"); c.reset()
            if (url.length === 0 || !isImageLoaded(url)) return
            c.save()
            c.beginPath(); c.arc(width / 2, height / 2, width / 2, 0, Math.PI * 2, false); c.closePath(); c.clip()
            c.drawImage(url, 0, 0, width, height)
            c.restore()
        }
    }
}
