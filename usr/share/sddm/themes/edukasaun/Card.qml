// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Glass card of the login screen (0.11 RC3): a see-through rounded card with
// a soft shadow and a light top edge. It rises into place once, after
// `delay` milliseconds. Children go inside, `padding` from the edge.
import QtQuick 2.15

Item {
    id: card
    property var theme
    default property alias content: inner.data
    property real padding: 18 * theme.s
    property real radius: 26 * theme.s
    property int delay: 0
    property real rise: 18

    opacity: 0
    transform: Translate { y: card.rise * card.theme.s }

    // Two soft shadow layers (no graphical effects module is needed).
    Rectangle {
        visible: !card.theme.contrast
        x: -2 * card.theme.s; y: 10 * card.theme.s
        width: parent.width + 4 * card.theme.s; height: parent.height
        radius: card.radius + 2 * card.theme.s
        color: card.theme.cardShadow; opacity: 0.55
    }
    Rectangle {
        visible: !card.theme.contrast
        y: 4 * card.theme.s
        width: parent.width; height: parent.height
        radius: card.radius
        color: card.theme.cardShadow
    }
    Rectangle {
        anchors.fill: parent
        radius: card.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: card.theme.cardTop }
            GradientStop { position: 1.0; color: card.theme.cardBottom }
        }
        border.color: card.theme.cardBorder
        border.width: card.theme.contrast ? 2 : 1
    }
    // The light top edge of the glass.
    Rectangle {
        visible: !card.theme.contrast && !card.theme.dark
        anchors.top: parent.top; anchors.topMargin: 1
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.max(0, parent.width - 2 * card.radius); height: 1
        color: "#ffffff"
    }
    Item {
        id: inner
        anchors.fill: parent
        anchors.margins: card.padding
    }

    SequentialAnimation {
        id: intro
        PauseAnimation { duration: card.delay }
        ParallelAnimation {
            NumberAnimation { target: card; property: "opacity"; from: 0; to: 1; duration: 320; easing.type: Easing.OutCubic }
            NumberAnimation { target: card; property: "rise"; to: 0; duration: 460; easing.type: Easing.OutCubic }
        }
    }
    Component.onCompleted: intro.start()
}
