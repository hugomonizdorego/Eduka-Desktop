// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Big tile of the System card (0.11 RC3): sleep, hibernate, restart or shut
// down with one click, in the colors of the Eduka leave screen.
import QtQuick 2.15

Rectangle {
    id: tile
    property var theme
    property string icon: ""
    property string label: ""
    property color tint: "#e5484d"
    property bool allowed: true
    signal activated()

    readonly property bool hot: area.containsMouse || activeFocus
    radius: 16 * theme.s
    color: theme.contrast ? (hot ? "#ffd400" : "#000000")
         : (hot ? tint : (theme.dark ? Qt.rgba(tint.r, tint.g, tint.b, 0.26) : Qt.tint("#ffffff", Qt.rgba(tint.r, tint.g, tint.b, 0.22))))
    border.color: theme.contrast ? "#ffffff" : (hot ? Qt.darker(tint, 1.12) : Qt.rgba(tint.r, tint.g, tint.b, theme.dark ? 0.5 : 0.4))
    border.width: theme.contrast ? 2 : 1
    opacity: allowed ? 1 : 0.45
    scale: area.pressed ? 0.95 : 1
    activeFocusOnTab: true
    Behavior on color { ColorAnimation { duration: 120 } }
    Behavior on scale { NumberAnimation { duration: 90 } }
    Accessible.role: Accessible.Button
    Accessible.name: label
    Accessible.onPressAction: if (tile.allowed) tile.activated()
    Keys.onReturnPressed: if (tile.allowed) tile.activated()
    Keys.onEnterPressed: if (tile.allowed) tile.activated()
    Keys.onSpacePressed: if (tile.allowed) tile.activated()

    Column {
        anchors.centerIn: parent
        width: parent.width - 8 * tile.theme.s
        spacing: 5 * tile.theme.s
        Icon {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 22 * tile.theme.s; height: width
            name: tile.icon
            ink: tile.hot ? (tile.theme.contrast ? "#000000" : "white")
                          : (tile.theme.contrast ? "#ffffff" : (tile.theme.dark ? Qt.lighter(tile.tint, 1.3) : Qt.darker(tile.tint, 1.18)))
        }
        Text {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            text: tile.label
            color: tile.hot ? (tile.theme.contrast ? "#000000" : "white") : tile.theme.textColor
            font.pixelSize: 11.5 * tile.theme.s; font.bold: true
        }
    }
    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: tile.allowed ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: if (tile.allowed) tile.activated()
    }
}
