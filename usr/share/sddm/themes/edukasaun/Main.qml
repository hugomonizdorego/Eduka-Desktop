// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Edukasaun OS login screen for SDDM (0.9.19; official logo since 0.11;
// glass "bento" cards since 0.11 RC3).
// Plain QtQuick items only, so it runs on the Qt 5 and the Qt 6 greeter.
//
// Settings (theme.conf, overridden by theme.conf.user written by
// Eduka-Settings → Login Screen):
//   style=light|dark|glass|pastel  accent=#rrggbb  title=…  showClock=true|false
//   background=/usr/share/Edukasaun/SDDM/Default.png  logo=…  defaultUser=…
//
// Four glass cards in the middle of the screen:
//   Sign in  the user (picked from the list or typed in) and the password
//   Clock    the time and a greeting (hidden with showClock=false)
//   Profile  the picture of the user, the day and the date
//   System   sleep, restart and shut down with one click, and the session
// and a round rail beside them: language, keyboard layout, on-screen
// keyboard and accessibility (larger text, high contrast). Everything
// scales with the screen, so the cards fit a small laptop, a tablet
// standing up and a large monitor alike.
//
// The language chosen here is used by this screen and, when the greeter may
// write files (QML_XHR_ALLOW_FILE_WRITE, set in /etc/sddm.conf.d/10-edukasaun.conf),
// by the Eduka-Desktop session after login: the greeter writes the user name
// and the language to /var/lib/edukasaun-desktop/login/language and
// eduka-desktop-session checks both before it uses them.

import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1366
    height: 768
    color: "#1f6b45"

    // ------------------------------------------------------------ settings
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string style: ["light", "dark", "glass", "pastel"].indexOf(String(config.style)) >= 0 ? String(config.style) : "light"
    property bool contrast: false
    property bool largeText: false
    property bool dark: style === "dark"
    property bool glass: style === "glass"
    property bool pastel: style === "pastel"
    property color accent: contrast ? "#ffd400" : (/^#[0-9a-fA-F]{6}$/.test(String(config.accent)) ? String(config.accent) : (dark ? "#26a69a" : (glass ? "#1e9bd7" : (pastel ? "#3fa684" : "#00a879"))))
    property bool showClock: String(config.showClock) !== "false"
    property bool busy: false
    property bool menuOpen: menus.open !== ""
    // One size unit. The cards and the rail (about 730 x 420 at s = 1)
    // always fit the screen; larger text makes them bigger when there is room.
    readonly property real textScale: largeText ? 1.2 : 1.0
    property real s: Math.max(0.6, Math.min(1.3 * textScale, height / 768 * textScale, (width - 24) / 760, (height - 24) / 470))

    // Glass cards: lighter at the top, a little more see-through below.
    property color cardTop: contrast ? "#000000" : (dark ? "#cc262e2c" : (glass ? "#99ffffff" : (pastel ? "#d9ffffff" : "#ebffffff")))
    property color cardBottom: contrast ? "#000000" : (dark ? "#b3151b1a" : (glass ? "#66ffffff" : (pastel ? "#a6ffffff" : "#c7ffffff")))
    property color cardBorder: contrast ? "#ffffff" : (dark ? "#2effffff" : (glass ? "#ccffffff" : "#f2ffffff"))
    property color cardShadow: contrast ? "transparent" : (dark ? "#59000000" : (pastel ? "#1f2f6f5c" : "#2410231e"))
    // The user and password fields are filled with the accent color.
    property color fieldColor: contrast ? "#000000" : Qt.darker(accent, 1.18)
    property color fieldHover: contrast ? "#1f1f1f" : Qt.darker(accent, 1.06)
    property color fieldText: "#ffffff"
    property color fieldHint: contrast ? "#ffd400" : "#e0ffffff"
    property color textColor: contrast ? "#ffffff" : (dark ? "#ffffff" : (pastel ? "#1f3d36" : "#10231e"))
    property color subColor: contrast ? "#ffffff" : (dark ? "#b3ffffff" : (pastel ? "#557069" : "#4d625c"))
    property color hoverColor: contrast ? "#333333" : (dark ? "#1affffff" : Qt.rgba(accent.r, accent.g, accent.b, 0.14))
    property color menuColor: contrast ? "#000000" : (dark ? "#202625" : "#fdfefd")

    // ------------------------------------------------------------ language
    // Language of this screen: the one picked in the menu, else the system's.
    property string language: ""
    property string lang: language.length > 0 ? language : String(Qt.locale().name)
    readonly property var languages: [
        { code: "", name: "System language" },
        { code: "en_US", name: "English" },
        { code: "pt_PT", name: "Português (Portugal)" },
        { code: "pt_BR", name: "Português (Brasil)" },
        { code: "tet", name: "Tetun" },
        { code: "id_ID", name: "Bahasa Indonesia" },
        { code: "ms_MY", name: "Bahasa Melayu" },
        { code: "tl_PH", name: "Filipino" },
        { code: "th_TH", name: "ไทย" },
        { code: "vi_VN", name: "Tiếng Việt" },
        { code: "zh_CN", name: "简体中文" },
        { code: "zh_TW", name: "繁體中文" }
    ]
    readonly property var strings: ({
        pt: { "Password or fingerprint": "Palavra-passe ou impressão digital", "Touch the fingerprint reader…": "Toque no leitor de impressões digitais…", "Sign in with fingerprint": "Entrar com a impressão digital", "Sign in": "Entrar", "Good morning": "Bom dia", "Good afternoon": "Boa tarde", "Good evening": "Boa noite", "Sign in to Eduka-Desktop": "Entrar no Eduka-Desktop", "User name": "Nome de utilizador", "Password": "Palavra-passe",
              "Other user…": "Outro utilizador…", "Back": "Voltar", "Caps Lock is on": "Caps Lock está ativo",
              "Wrong user name or password. Please try again.": "Nome de utilizador ou palavra-passe errados. Tente novamente.",
              "Signing in…": "A entrar…", "Language": "Idioma", "System language": "Idioma do sistema", "Keyboard": "Teclado",
              "Accessibility": "Acessibilidade", "Larger text": "Texto maior", "High contrast": "Alto contraste",
              "On-screen keyboard": "Teclado no ecrã", "Not installed": "Não instalado", "Power": "Energia",
              "Suspend": "Suspender", "Hibernate": "Hibernar", "Restart": "Reiniciar", "Shut Down": "Desligar",
              "Session": "Sessão", "Used on this screen and on the desktop after you sign in.": "Usado neste ecrã e no ambiente de trabalho depois de entrar." },
        pt_BR: { "Password or fingerprint": "Senha ou impressão digital", "User name": "Nome de usuário", "Password": "Senha", "Other user…": "Outro usuário…",
              "Wrong user name or password. Please try again.": "Nome de usuário ou senha incorretos. Tente novamente.",
              "Signing in…": "Entrando…", "On-screen keyboard": "Teclado na tela",
              "Used on this screen and on the desktop after you sign in.": "Usado nesta tela e na área de trabalho depois de entrar." },
        tet: { "Password or fingerprint": "Liafuan-xave ka marka-liman", "Touch the fingerprint reader…": "Kona leitor marka-liman…", "Sign in with fingerprint": "Tama ho marka-liman", "Sign in": "Tama", "Good morning": "Dader di'ak", "Good afternoon": "Loraik di'ak", "Good evening": "Kalan di'ak", "Sign in to Eduka-Desktop": "Tama ba Eduka-Desktop", "User name": "Naran uza-na'in", "Password": "Liafuan-xave",
              "Other user…": "Uza-na'in seluk…", "Back": "Fila", "Caps Lock is on": "Caps Lock moris",
              "Wrong user name or password. Please try again.": "Naran ka liafuan-xave sala. Koko fali.",
              "Signing in…": "Tama hela…", "Language": "Lian", "System language": "Lian sistema", "Keyboard": "Tekladu",
              "Accessibility": "Asesibilidade", "Larger text": "Testu boot liu", "High contrast": "Kontraste aas",
              "On-screen keyboard": "Tekladu iha ekran", "Not installed": "La instala", "Power": "Enerjia",
              "Suspend": "Suspende", "Hibernate": "Iberna", "Restart": "Hahú fali", "Shut Down": "Hamate",
              "Session": "Sesaun", "Used on this screen and on the desktop after you sign in.": "Uza iha ekran ida-ne'e no iha desktop hafoin tama." },
        id: { "Password or fingerprint": "Kata sandi atau sidik jari", "Touch the fingerprint reader…": "Sentuh pemindai sidik jari…", "Sign in with fingerprint": "Masuk dengan sidik jari", "Sign in": "Masuk", "Good morning": "Selamat pagi", "Good afternoon": "Selamat siang", "Good evening": "Selamat malam", "Sign in to Eduka-Desktop": "Masuk ke Eduka-Desktop", "User name": "Nama pengguna", "Password": "Kata sandi",
              "Other user…": "Pengguna lain…", "Back": "Kembali", "Caps Lock is on": "Caps Lock aktif",
              "Wrong user name or password. Please try again.": "Nama pengguna atau kata sandi salah. Coba lagi.",
              "Signing in…": "Sedang masuk…", "Language": "Bahasa", "System language": "Bahasa sistem", "Keyboard": "Papan ketik",
              "Accessibility": "Aksesibilitas", "Larger text": "Teks lebih besar", "High contrast": "Kontras tinggi",
              "On-screen keyboard": "Papan ketik layar", "Not installed": "Belum terpasang", "Power": "Daya",
              "Suspend": "Tidur", "Hibernate": "Hibernasi", "Restart": "Mulai Ulang", "Shut Down": "Matikan",
              "Session": "Sesi", "Used on this screen and on the desktop after you sign in.": "Dipakai di layar ini dan di desktop setelah masuk." },
        ms: { "Password or fingerprint": "Kata laluan atau cap jari", "Touch the fingerprint reader…": "Sentuh pengimbas cap jari…", "Sign in with fingerprint": "Log masuk dengan cap jari", "Sign in": "Log masuk", "Good morning": "Selamat pagi", "Good afternoon": "Selamat petang", "Good evening": "Selamat malam", "Sign in to Eduka-Desktop": "Log masuk ke Eduka-Desktop", "User name": "Nama pengguna", "Password": "Kata laluan",
              "Other user…": "Pengguna lain…", "Back": "Kembali", "Caps Lock is on": "Caps Lock dihidupkan",
              "Wrong user name or password. Please try again.": "Nama pengguna atau kata laluan salah. Cuba lagi.",
              "Signing in…": "Sedang log masuk…", "Language": "Bahasa", "System language": "Bahasa sistem", "Keyboard": "Papan kekunci",
              "Accessibility": "Kebolehcapaian", "Larger text": "Teks lebih besar", "High contrast": "Kontras tinggi",
              "On-screen keyboard": "Papan kekunci skrin", "Not installed": "Tidak dipasang", "Power": "Kuasa",
              "Suspend": "Tangguh", "Hibernate": "Hibernasi", "Restart": "Mula Semula", "Shut Down": "Matikan",
              "Session": "Sesi", "Used on this screen and on the desktop after you sign in.": "Digunakan pada skrin ini dan pada desktop selepas log masuk." },
        tl: { "Password or fingerprint": "Password o fingerprint", "Touch the fingerprint reader…": "Pindutin ang fingerprint reader…", "Sign in with fingerprint": "Mag-sign in gamit ang fingerprint", "Sign in": "Mag-sign in", "Good morning": "Magandang umaga", "Good afternoon": "Magandang hapon", "Good evening": "Magandang gabi", "Sign in to Eduka-Desktop": "Mag-sign in sa Eduka-Desktop", "User name": "Pangalan ng user", "Password": "Password",
              "Other user…": "Ibang user…", "Back": "Bumalik", "Caps Lock is on": "Naka-on ang Caps Lock",
              "Wrong user name or password. Please try again.": "Mali ang pangalan o password. Subukan muli.",
              "Signing in…": "Nagsa-sign in…", "Language": "Wika", "System language": "Wika ng system", "Keyboard": "Keyboard",
              "Accessibility": "Accessibility", "Larger text": "Mas malaking teksto", "High contrast": "Mataas na contrast",
              "On-screen keyboard": "On-screen keyboard", "Not installed": "Hindi naka-install", "Power": "Power",
              "Suspend": "I-suspend", "Hibernate": "I-hibernate", "Restart": "I-restart", "Shut Down": "I-shut Down",
              "Session": "Session", "Used on this screen and on the desktop after you sign in.": "Gagamitin dito at sa desktop pagkatapos mag-sign in." },
        th: { "Password or fingerprint": "รหัสผ่านหรือลายนิ้วมือ", "Touch the fingerprint reader…": "แตะเครื่องสแกนลายนิ้วมือ…", "Sign in with fingerprint": "เข้าสู่ระบบด้วยลายนิ้วมือ", "Sign in": "เข้าสู่ระบบ", "Good morning": "สวัสดีตอนเช้า", "Good afternoon": "สวัสดีตอนบ่าย", "Good evening": "สวัสดีตอนเย็น", "Sign in to Eduka-Desktop": "เข้าสู่ระบบ Eduka-Desktop", "User name": "ชื่อผู้ใช้", "Password": "รหัสผ่าน",
              "Other user…": "ผู้ใช้อื่น…", "Back": "ย้อนกลับ", "Caps Lock is on": "Caps Lock เปิดอยู่",
              "Wrong user name or password. Please try again.": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง",
              "Signing in…": "กำลังเข้าสู่ระบบ…", "Language": "ภาษา", "System language": "ภาษาของระบบ", "Keyboard": "แป้นพิมพ์",
              "Accessibility": "การช่วยการเข้าถึง", "Larger text": "ตัวอักษรใหญ่ขึ้น", "High contrast": "คอนทราสต์สูง",
              "On-screen keyboard": "แป้นพิมพ์บนหน้าจอ", "Not installed": "ไม่ได้ติดตั้ง", "Power": "พลังงาน",
              "Suspend": "พักเครื่อง", "Hibernate": "ไฮเบอร์เนต", "Restart": "เริ่มใหม่", "Shut Down": "ปิดเครื่อง",
              "Session": "เซสชัน", "Used on this screen and on the desktop after you sign in.": "ใช้กับหน้าจอนี้และเดสก์ท็อปหลังเข้าสู่ระบบ" },
        vi: { "Password or fingerprint": "Mật khẩu hoặc vân tay", "Touch the fingerprint reader…": "Chạm vào đầu đọc vân tay…", "Sign in with fingerprint": "Đăng nhập bằng vân tay", "Sign in": "Đăng nhập", "Good morning": "Chào buổi sáng", "Good afternoon": "Chào buổi chiều", "Good evening": "Chào buổi tối", "Sign in to Eduka-Desktop": "Đăng nhập vào Eduka-Desktop", "User name": "Tên người dùng", "Password": "Mật khẩu",
              "Other user…": "Người dùng khác…", "Back": "Quay lại", "Caps Lock is on": "Caps Lock đang bật",
              "Wrong user name or password. Please try again.": "Sai tên người dùng hoặc mật khẩu. Vui lòng thử lại.",
              "Signing in…": "Đang đăng nhập…", "Language": "Ngôn ngữ", "System language": "Ngôn ngữ hệ thống", "Keyboard": "Bàn phím",
              "Accessibility": "Trợ năng", "Larger text": "Chữ lớn hơn", "High contrast": "Độ tương phản cao",
              "On-screen keyboard": "Bàn phím ảo", "Not installed": "Chưa cài đặt", "Power": "Nguồn",
              "Suspend": "Tạm ngưng", "Hibernate": "Ngủ đông", "Restart": "Khởi động lại", "Shut Down": "Tắt máy",
              "Session": "Phiên", "Used on this screen and on the desktop after you sign in.": "Dùng cho màn hình này và màn hình nền sau khi đăng nhập." },
        zh_CN: { "Password or fingerprint": "密码或指纹", "Touch the fingerprint reader…": "请触摸指纹识别器…", "Sign in with fingerprint": "使用指纹登录", "Sign in": "登录", "Good morning": "早上好", "Good afternoon": "下午好", "Good evening": "晚上好", "Sign in to Eduka-Desktop": "登录 Eduka-Desktop", "User name": "用户名", "Password": "密码",
              "Other user…": "其他用户…", "Back": "返回", "Caps Lock is on": "大写锁定已打开",
              "Wrong user name or password. Please try again.": "用户名或密码错误，请重试。",
              "Signing in…": "正在登录…", "Language": "语言", "System language": "系统语言", "Keyboard": "键盘",
              "Accessibility": "无障碍", "Larger text": "大号文字", "High contrast": "高对比度",
              "On-screen keyboard": "屏幕键盘", "Not installed": "未安装", "Power": "电源",
              "Suspend": "挂起", "Hibernate": "休眠", "Restart": "重新启动", "Shut Down": "关机",
              "Session": "会话", "Used on this screen and on the desktop after you sign in.": "用于此屏幕以及登录后的桌面。" },
        zh_TW: { "Password or fingerprint": "密碼或指紋", "Touch the fingerprint reader…": "請觸碰指紋辨識器…", "Sign in with fingerprint": "使用指紋登入", "Sign in": "登入", "Good morning": "早安", "Good afternoon": "午安", "Good evening": "晚上好", "Sign in to Eduka-Desktop": "登入 Eduka-Desktop", "User name": "使用者名稱", "Password": "密碼",
              "Other user…": "其他使用者…", "Back": "返回", "Caps Lock is on": "大寫鎖定已開啟",
              "Wrong user name or password. Please try again.": "使用者名稱或密碼錯誤，請再試一次。",
              "Signing in…": "正在登入…", "Language": "語言", "System language": "系統語言", "Keyboard": "鍵盤",
              "Accessibility": "無障礙", "Larger text": "較大文字", "High contrast": "高對比",
              "On-screen keyboard": "螢幕鍵盤", "Not installed": "未安裝", "Power": "電源",
              "Suspend": "暫停", "Hibernate": "休眠", "Restart": "重新啟動", "Shut Down": "關機",
              "Session": "工作階段", "Used on this screen and on the desktop after you sign in.": "用於此畫面以及登入後的桌面。" }
    })

    function tr(text) {
        var l = root.lang.split(".")[0].split("@")[0]
        var base = l.split("_")[0]
        var full = strings[l]
        if (full && full[text] !== undefined) return full[text]
        if (l.indexOf("zh") === 0 && strings[l] === undefined) {
            var zh = (l === "zh_HK" || l === "zh_MO") ? strings["zh_TW"] : strings["zh_CN"]
            if (zh[text] !== undefined) return zh[text]
        }
        var b = strings[base]
        if (b && b[text] !== undefined) return b[text]
        if (base === "tet" && strings["pt"][text] !== undefined) return strings["pt"][text]
        return text
    }

    function languageName(code) {
        if (code === "") return tr("Language")
        for (var i = 0; i < languages.length; i++) if (languages[i].code === code) return languages[i].name
        return code
    }
    // Short code under the globe of the rail: EN, PT, TET, ID, …
    function languageCode() {
        var l = root.lang.split(".")[0].split("@")[0].split("_")[0]
        return l.length > 0 && l !== "C" ? l.toUpperCase() : "EN"
    }

    // The greeter remembers the language it last wrote (read access needs
    // QML_XHR_ALLOW_FILE_READ; without it the system language is used).
    readonly property string langFile: "file:///var/lib/edukasaun-desktop/login/language"
    function loadLanguage() {
        try {
            var x = new XMLHttpRequest()
            x.onreadystatechange = function() {
                if (x.readyState !== XMLHttpRequest.DONE) return
                var m = /(^|\n)lang=([A-Za-z_]{2,6})/.exec(String(x.responseText))
                if (m && languages.some(function(l) { return l.code === m[2] })) root.language = m[2]
            }
            x.open("GET", langFile); x.send()
        } catch (e) {}
    }
    function saveLanguage(name) {
        try {
            var x = new XMLHttpRequest()
            x.open("PUT", langFile)
            x.send("user=" + name + "\nlang=" + root.language + "\n")
        } catch (e) {}
    }

    // ------------------------------------------------------------ fingerprint
    // Eduka-Settings → Fingerprint writes this flag when fingerprint login is
    // on (0.11 RC3). The password is checked first (the Edukasaun PAM
    // profile); an empty password goes on to the fingerprint reader.
    property bool fingerprint: false
    function loadFingerprint() {
        try {
            var x = new XMLHttpRequest()
            x.onreadystatechange = function() {
                if (x.readyState === XMLHttpRequest.DONE) root.fingerprint = /^on/.test(String(x.responseText))
            }
            x.open("GET", "file:///var/lib/edukasaun-desktop/login/fingerprint"); x.send()
        } catch (e) {}
    }
    function fingerLogin() {
        if (busy) return
        password.text = ""
        doLogin()
        if (busy) message.text = root.tr("Touch the fingerprint reader…")
    }

    // ------------------------------------------------------------ users
    property var userList: []          // [{ name, real, icon }] from SDDM's user list
    property int userIndex: -1
    property bool manualUser: false
    readonly property var currentUser: !manualUser && userIndex >= 0 && userIndex < userList.length ? userList[userIndex] : null
    readonly property string userName: currentUser ? currentUser.name : ""
    readonly property string displayName: currentUser ? (currentUser.real.length > 0 ? currentUser.real : currentUser.name) : userField.text
    readonly property string firstName: displayName.split(" ")[0]

    Repeater {
        model: userModel
        delegate: Item {
            Component.onCompleted: {
                var l = root.userList.slice()
                l[index] = { name: String(model.name), real: model.realName ? String(model.realName) : "", icon: model.icon ? String(model.icon) : "" }
                root.userList = l
            }
        }
    }

    function indexOfUser(name) {
        for (var i = 0; i < userList.length; i++) if (userList[i].name === name) return i
        return -1
    }
    function pickInitialUser() {
        var last = userModel.lastUser ? String(userModel.lastUser) : ""
        var wanted = config.defaultUser ? String(config.defaultUser) : ""
        if (userList.length === 0) { manualUser = true; userField.text = last; return }
        var idx = last.length > 0 ? indexOfUser(last) : -1
        if (idx < 0 && wanted.length > 0) idx = indexOfUser(wanted)
        if (idx < 0) idx = userModel.lastIndex >= 0 && userModel.lastIndex < userList.length ? userModel.lastIndex : 0
        userIndex = idx
    }
    function chooseUser(i) {
        if (i < 0 || i >= userList.length) return
        manualUser = false
        userIndex = i
        password.text = ""; message.text = ""
        password.forceActiveFocus()
    }
    function otherUser() {
        manualUser = true
        userField.text = ""; password.text = ""; message.text = ""
        userField.forceActiveFocus()
    }
    // Up and Down (or Left and Right in an empty password field) change the user.
    function stepUser(d) {
        if (manualUser || userList.length < 2) return false
        chooseUser((userIndex + d + userList.length) % userList.length)
        return true
    }

    function doLogin() {
        if (busy) return
        var name = manualUser ? userField.text : root.userName
        if (name.length === 0) { userField.forceActiveFocus(); return }
        message.text = ""
        busy = true
        saveLanguage(name)
        sddm.login(name, password.text, root.sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginSucceeded() { root.busy = false }
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            message.text = root.tr("Wrong user name or password. Please try again.")
            shake.start()
            password.forceActiveFocus()
        }
        function onInformationMessage(text) { message.text = text }
    }

    // ------------------------------------------------------------ time
    property int hour: 12
    readonly property string greeting: {
        var g = hour < 5 ? "Good evening" : (hour < 12 ? "Good morning" : (hour < 18 ? "Good afternoon" : "Good evening"))
        return firstName.length > 0 ? tr(g) + ", " + firstName : tr(g)
    }
    Timer {
        interval: 1000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: {
            var now = new Date()
            var loc = Qt.locale(root.lang.indexOf("tet") === 0 ? "pt_PT" : root.lang)
            root.hour = now.getHours()
            clockTime.text = Qt.formatTime(now, "HH:mm")
            dayText.text = now.toLocaleDateString(loc, "ddd").replace(/\.$/, "").toUpperCase()
            dateText.text = now.toLocaleDateString(loc, "d MMMM yyyy")
        }
    }

    // ------------------------------------------------------------ background
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.dark ? "#2f3b39" : (root.glass ? "#bfe3f5" : (root.pastel ? "#d6e8f8" : "#e9f6c9")) }
            GradientStop { position: 0.5; color: root.dark ? "#1f2a28" : (root.glass ? "#7fb9dc" : (root.pastel ? "#edf7f2" : "#8fcf7a")) }
            GradientStop { position: 1.0; color: root.dark ? "#121616" : (root.glass ? "#2f6f9a" : (root.pastel ? "#d6efe6" : "#1f6b45")) }
        }
    }
    // Soft lights in the colors of Eduka-Desktop behind the glass (only
    // without a picture; painted once).
    Canvas {
        id: lights
        anchors.fill: parent
        visible: !root.contrast && !background.visible
        property string look: root.style
        onLookChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            var c = getContext("2d"); c.reset()
            var w = width, h = height, m = Math.max(w, h)
            var set = root.dark ? [[0.14, 0.86, 0.42, "38,166,154", 0.24], [0.86, 0.14, 0.38, "124,108,240", 0.18], [0.9, 0.88, 0.28, "229,72,77", 0.10]]
                    : root.glass ? [[0.16, 0.18, 0.4, "255,255,255", 0.40], [0.86, 0.82, 0.45, "30,155,215", 0.35], [0.82, 0.14, 0.3, "185,167,240", 0.28]]
                    : root.pastel ? [[0.12, 0.86, 0.42, "63,166,132", 0.40], [0.88, 0.12, 0.40, "124,196,240", 0.50], [0.92, 0.9, 0.30, "246,178,107", 0.32], [0.06, 0.08, 0.28, "185,167,240", 0.34], [0.5, 0.5, 0.28, "255,255,255", 0.40]]
                    : [[0.1, 0.9, 0.45, "0,168,121", 0.35], [0.9, 0.12, 0.40, "255,255,255", 0.45], [0.88, 0.9, 0.30, "246,178,107", 0.26]]
            for (var i = 0; i < set.length; i++) {
                var b = set[i], x = b[0] * w, y = b[1] * h, r = b[2] * m
                var g = c.createRadialGradient(x, y, 0, x, y, r)
                g.addColorStop(0, "rgba(" + b[3] + "," + b[4] + ")")
                g.addColorStop(1, "rgba(" + b[3] + ",0)")
                c.fillStyle = g
                c.fillRect(x - r, y - r, r * 2, r * 2)
            }
        }
    }
    Image {
        id: background
        anchors.fill: parent
        source: config.background ? "file://" + config.background : ""
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        visible: status === Image.Ready && !root.contrast
        smooth: true
    }
    // A soft shade over a picture keeps the glass cards readable.
    Rectangle {
        anchors.fill: parent
        visible: !root.contrast && (background.visible || root.dark)
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.dark ? "#73000000" : (root.pastel ? "#402f5f78" : "#33000000") }
            GradientStop { position: 0.5; color: root.dark ? "#40000000" : "#0d000000" }
            GradientStop { position: 1.0; color: root.dark ? "#80000000" : (root.pastel ? "#332f6f5c" : "#40000000") }
        }
    }
    Rectangle { anchors.fill: parent; visible: root.contrast; color: "#000000" }

    // Click anywhere outside an open menu closes it.
    MouseArea {
        anchors.fill: parent
        enabled: menus.open !== ""
        onClicked: menus.open = ""
    }

    // ------------------------------------------------------------ cards
    Item {
        id: bento
        readonly property real gap: 14 * root.s
        readonly property real colW: 300 * root.s
        readonly property real leftNeed: signIn.need + (root.showClock ? gap + clockCard.need : 0)
        readonly property real rightNeed: profile.need + gap + system.need
        readonly property real oskHeight: osk.shown && osk.available ? osk.height : 0
        width: colW * 2 + gap
        height: Math.max(leftNeed, rightNeed)
        x: Math.round((parent.width - width - gap - rail.width) / 2)
        y: Math.round(Math.max(12, (parent.height - oskHeight - height) / 2))
        Behavior on y { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

        // ---- Sign in
        Card {
            id: signIn
            theme: root
            property real shakeX: 0
            readonly property real need: signInBody.implicitHeight + 2 * padding
            x: shakeX; y: 0
            width: bento.colW
            height: root.showClock ? need : bento.height
            delay: 0

            SequentialAnimation {
                id: shake
                NumberAnimation { target: signIn; property: "shakeX"; to: -12; duration: 50 }
                NumberAnimation { target: signIn; property: "shakeX"; to: 12; duration: 70 }
                NumberAnimation { target: signIn; property: "shakeX"; to: -6; duration: 60 }
                NumberAnimation { target: signIn; property: "shakeX"; to: 0; duration: 50 }
            }

            Column {
                id: signInBody
                width: parent.width
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10 * root.s

                Text {
                    width: parent.width; horizontalAlignment: Text.AlignHCenter
                    text: root.tr("Sign in")
                    color: root.textColor; font.pixelSize: 26 * root.s; font.weight: Font.Normal
                    bottomPadding: 4 * root.s
                    elide: Text.ElideRight
                }

                // The user: picked from the list, or typed in ("Other user…").
                Rectangle {
                    id: userBox
                    width: parent.width; height: 56 * root.s; radius: 16 * root.s
                    color: !root.manualUser && userArea.containsMouse ? root.fieldHover : root.fieldColor
                    border.color: root.contrast ? (userField.activeFocus ? "#ffd400" : "#ffffff") : "#ffffff"
                    border.width: root.contrast ? 2 : (userField.activeFocus || menus.open === "user" ? 2 : 0)
                    Accessible.role: root.manualUser ? Accessible.EditableText : Accessible.ComboBox
                    Accessible.name: root.tr("User name")

                    Avatar {
                        id: smallFace
                        visible: !root.manualUser
                        theme: root; ring: 2; ringColor: "#ffffff"
                        x: 10 * root.s; anchors.verticalCenter: parent.verticalCenter
                        width: 36 * root.s; height: width
                        source: root.currentUser ? root.currentUser.icon : ""
                        name: root.displayName
                    }
                    Column {
                        anchors.left: root.manualUser ? parent.left : smallFace.right
                        anchors.leftMargin: root.manualUser ? 16 * root.s : 10 * root.s
                        anchors.right: userSide.left; anchors.rightMargin: 6 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1 * root.s
                        Text { text: root.tr("User name"); color: root.fieldHint; font.pixelSize: 10.5 * root.s; font.bold: true }
                        Text {
                            visible: !root.manualUser
                            width: parent.width; elide: Text.ElideRight
                            text: root.displayName
                            color: root.fieldText; font.pixelSize: 15 * root.s; font.bold: true
                        }
                        TextInput {
                            id: userField
                            visible: root.manualUser
                            width: parent.width; height: 22 * root.s
                            verticalAlignment: TextInput.AlignVCenter
                            font.pixelSize: 15 * root.s; font.bold: true; color: root.fieldText
                            selectionColor: "#ffffff"; selectedTextColor: root.fieldColor
                            clip: true
                            KeyNavigation.tab: password
                            Keys.onReturnPressed: password.forceActiveFocus()
                            Keys.onEnterPressed: password.forceActiveFocus()
                            Keys.onEscapePressed: function(event) {
                                if (menus.open !== "") { menus.open = ""; return }
                                if (root.userList.length > 0) root.chooseUser(Math.max(0, root.userIndex))
                            }
                        }
                    }
                    // Right side: the list of users, or back to it.
                    Item {
                        id: userSide
                        anchors.right: parent.right; anchors.rightMargin: 8 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        width: root.userList.length > 0 ? 34 * root.s : 0; height: 34 * root.s
                        visible: root.userList.length > 0
                        Rectangle {
                            anchors.fill: parent; radius: width / 2
                            visible: root.manualUser
                            color: backArea.containsMouse ? "#40ffffff" : "#1fffffff"
                        }
                        Icon {
                            anchors.centerIn: parent
                            width: 16 * root.s; height: width
                            name: root.manualUser ? "back" : "updown"; ink: root.fieldText
                        }
                        MouseArea {
                            id: backArea
                            anchors.fill: parent
                            enabled: root.manualUser
                            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onClicked: root.chooseUser(Math.max(0, root.userIndex))
                        }
                    }
                    MouseArea {
                        id: userArea
                        anchors.fill: parent
                        enabled: !root.manualUser && root.userList.length > 0
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: menus.toggle("user")
                    }
                }

                // The password, with the round sign-in button.
                Rectangle {
                    id: passBox
                    width: parent.width; height: 56 * root.s; radius: 16 * root.s
                    color: root.fieldColor
                    border.color: root.contrast ? (password.activeFocus ? "#ffd400" : "#ffffff") : "#ffffff"
                    border.width: root.contrast || password.activeFocus ? 2 : 0
                    Text {
                        id: passCaption
                        x: 16 * root.s; y: 9 * root.s
                        text: root.busy ? root.tr("Signing in…") : (root.fingerprint ? root.tr("Password or fingerprint") : root.tr("Password"))
                        color: root.fieldHint; font.pixelSize: 10.5 * root.s; font.bold: true
                    }
                    TextInput {
                        id: password
                        anchors.left: parent.left; anchors.leftMargin: 16 * root.s
                        anchors.right: finger.visible ? finger.left : go.left; anchors.rightMargin: 8 * root.s
                        anchors.top: passCaption.bottom; anchors.bottom: parent.bottom; anchors.bottomMargin: 6 * root.s
                        verticalAlignment: TextInput.AlignVCenter
                        font.pixelSize: 16 * root.s; color: root.fieldText
                        selectionColor: "#ffffff"; selectedTextColor: root.fieldColor
                        echoMode: TextInput.Password; passwordCharacter: "●"
                        clip: true; focus: true
                        Accessible.name: root.tr("Password")
                        KeyNavigation.backtab: root.manualUser ? userField : password
                        Keys.onReturnPressed: root.doLogin()
                        Keys.onEnterPressed: root.doLogin()
                        Keys.onUpPressed: function(event) { if (text.length > 0 || !root.stepUser(-1)) event.accepted = false }
                        Keys.onDownPressed: function(event) { if (text.length > 0 || !root.stepUser(1)) event.accepted = false }
                        Keys.onLeftPressed: function(event) { if (text.length > 0 || !root.stepUser(-1)) event.accepted = false }
                        Keys.onRightPressed: function(event) { if (text.length > 0 || !root.stepUser(1)) event.accepted = false }
                    }
                    // Sign in with the finger: an empty password, then the reader.
                    Rectangle {
                        id: finger
                        visible: root.fingerprint && !root.busy
                        anchors.right: go.left; anchors.rightMargin: 6 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        width: go.width; height: width; radius: width / 2
                        color: fingerArea.containsMouse ? "#40ffffff" : "#26ffffff"
                        border.color: "#80ffffff"; border.width: 1
                        Accessible.role: Accessible.Button
                        Accessible.name: root.tr("Sign in with fingerprint")
                        Icon { anchors.centerIn: parent; width: parent.width * 0.6; height: width; name: "finger"; ink: root.fieldText }
                        MouseArea { id: fingerArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.fingerLogin() }
                    }
                    Rectangle {
                        id: go
                        anchors.right: parent.right; anchors.rightMargin: 7 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.height - 14 * root.s; height: width; radius: width / 2
                        color: root.contrast ? "#ffd400" : (goArea.pressed ? "#e6ffffff" : "#ffffff")
                        scale: goArea.pressed ? 0.94 : (goArea.containsMouse ? 1.06 : 1)
                        Behavior on scale { NumberAnimation { duration: 90 } }
                        Accessible.role: Accessible.Button
                        Accessible.name: root.tr("Sign in")
                        Icon {
                            anchors.centerIn: parent; width: parent.width * 0.5; height: width
                            name: "arrow"; ink: root.contrast ? "#000000" : root.fieldColor
                            visible: !root.busy
                        }
                        Text { anchors.centerIn: parent; visible: root.busy; text: "…"; color: root.fieldColor; font.pixelSize: 18 * root.s; font.bold: true }
                        MouseArea { id: goArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.doLogin() }
                    }
                }

                Text {
                    width: parent.width; horizontalAlignment: Text.AlignHCenter
                    text: root.tr("Caps Lock is on")
                    color: root.contrast ? "#ffd400" : (root.dark ? "#ffe082" : "#8a5a00"); font.pixelSize: 12 * root.s; font.bold: true
                    visible: typeof keyboard !== "undefined" && keyboard.capsLock
                }
                Text {
                    id: message
                    width: parent.width; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                    color: root.contrast ? "#ff8080" : (root.dark ? "#ef9a9a" : "#b3261e"); font.pixelSize: 13 * root.s
                    visible: text.length > 0
                }
            }
        }

        // ---- Clock and greeting
        Card {
            id: clockCard
            theme: root
            visible: root.showClock
            readonly property real need: clockBody.implicitHeight + 2 * padding
            x: 0; y: signIn.height + bento.gap
            width: bento.colW
            height: Math.max(need, bento.height - y)
            delay: 120

            Column {
                id: clockBody
                anchors.centerIn: parent
                width: parent.width
                spacing: 2 * root.s
                Text {
                    id: clockTime
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: root.textColor; font.pixelSize: 58 * root.s; font.weight: Font.Light
                    font.letterSpacing: 2 * root.s
                }
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 6 * root.s
                    Icon {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 14 * root.s; height: width
                        name: "user"; ink: root.subColor
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        width: Math.min(implicitWidth, clockBody.width - 24 * root.s)
                        elide: Text.ElideRight
                        text: root.greeting
                        color: root.subColor; font.pixelSize: 13 * root.s
                    }
                }
            }
        }

        // ---- Profile: picture, day and date
        Card {
            id: profile
            theme: root
            readonly property real need: profileBody.implicitHeight + 2 * padding
            x: bento.colW + bento.gap; y: 0
            width: bento.colW
            height: need
            delay: 60

            Column {
                id: profileBody
                anchors.centerIn: parent
                spacing: 6 * root.s
                Item {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 104 * root.s; height: width
                    // A soft halo in the accent color around the picture.
                    Rectangle {
                        anchors.fill: parent
                        radius: width / 2
                        color: "transparent"
                        border.color: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, root.contrast ? 1 : 0.28)
                        border.width: 5 * root.s
                    }
                    Avatar {
                        id: bigFace
                        anchors.centerIn: parent
                        width: 90 * root.s; height: width
                        theme: root; ring: 3 * root.s
                        source: root.currentUser ? root.currentUser.icon : ""
                        name: root.displayName
                        MouseArea {
                            anchors.fill: parent
                            enabled: root.userList.length > 0
                            cursorShape: Qt.PointingHandCursor
                            onClicked: menus.toggle("user")
                        }
                    }
                }
                Text {
                    id: dayText
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: root.textColor; font.pixelSize: 28 * root.s; font.weight: Font.DemiBold
                    font.letterSpacing: 5 * root.s
                }
                Text {
                    id: dateText
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: root.subColor; font.pixelSize: 13 * root.s
                }
            }
        }

        // ---- System: power and session
        Card {
            id: system
            theme: root
            readonly property real need: systemBody.implicitHeight + 2 * padding
            x: profile.x; y: profile.height + bento.gap
            width: bento.colW
            height: Math.max(need, bento.height - y)
            delay: 180

            Column {
                id: systemBody
                width: parent.width
                anchors.verticalCenter: parent.verticalCenter
                spacing: 12 * root.s

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 10 * root.s
                    Image {
                        id: brandLogo
                        anchors.verticalCenter: parent.verticalCenter
                        width: 34 * root.s; height: width
                        source: "logo.png"; smooth: true; mipmap: true
                        fillMode: Image.PreserveAspectFit
                    }
                    Column {
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            text: config.title ? String(config.title) : "Edukasaun"
                            color: root.textColor; font.pixelSize: 16 * root.s; font.bold: true
                        }
                        Text {
                            visible: text.length > 0
                            text: sddm.hostName ? String(sddm.hostName) : ""
                            color: root.subColor; font.pixelSize: 11.5 * root.s
                        }
                    }
                }

                // One click: no menu, no second button.
                Grid {
                    id: tiles
                    width: parent.width
                    property var actions: {
                        var m = []
                        if (sddm.canSuspend) m.push({ key: "suspend", icon: "suspend", text: root.tr("Suspend"), tint: "#7c6cf0", ok: true })
                        if (sddm.canHibernate) m.push({ key: "hibernate", icon: "hibernate", text: root.tr("Hibernate"), tint: "#159a9c", ok: true })
                        m.push({ key: "reboot", icon: "restart", text: root.tr("Restart"), tint: "#f08c2e", ok: sddm.canReboot })
                        m.push({ key: "poweroff", icon: "power", text: root.tr("Shut Down"), tint: "#e5484d", ok: sddm.canPowerOff })
                        return m
                    }
                    columns: actions.length > 3 ? 2 : actions.length
                    spacing: 8 * root.s
                    Repeater {
                        model: tiles.actions
                        delegate: PowerTile {
                            theme: root
                            width: (tiles.width - (tiles.columns - 1) * tiles.spacing) / tiles.columns
                            height: 60 * root.s
                            icon: modelData.icon; label: modelData.text; tint: modelData.tint
                            allowed: modelData.ok
                            onActivated: {
                                menus.open = ""
                                if (modelData.key === "suspend") sddm.suspend()
                                else if (modelData.key === "hibernate") sddm.hibernate()
                                else if (modelData.key === "reboot") sddm.reboot()
                                else sddm.powerOff()
                            }
                        }
                    }
                }

                // The session (normally only Eduka-Desktop).
                Rectangle {
                    id: sessionPill
                    width: parent.width; height: 50 * root.s; radius: 16 * root.s
                    readonly property bool choice: sessionNames.names.length > 1
                    color: choice && sessionArea.containsMouse ? root.fieldHover : root.fieldColor
                    border.color: "#ffffff"
                    border.width: root.contrast ? 2 : (menus.open === "session" ? 2 : 0)
                    Accessible.role: Accessible.ComboBox
                    Accessible.name: root.tr("Session")
                    Icon {
                        id: sessionIcon
                        x: 14 * root.s; anchors.verticalCenter: parent.verticalCenter
                        width: 18 * root.s; height: width
                        name: "session"; ink: root.fieldText
                    }
                    Column {
                        anchors.left: sessionIcon.right; anchors.leftMargin: 10 * root.s
                        anchors.right: sessionChevron.left; anchors.rightMargin: 6 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        Text { text: root.tr("Session"); color: root.fieldHint; font.pixelSize: 10.5 * root.s; font.bold: true }
                        Text {
                            width: parent.width; elide: Text.ElideRight
                            text: sessionNames.names.length > root.sessionIndex ? sessionNames.names[root.sessionIndex] : "Eduka-Desktop"
                            color: root.fieldText; font.pixelSize: 14 * root.s; font.bold: true
                        }
                    }
                    Icon {
                        id: sessionChevron
                        anchors.right: parent.right; anchors.rightMargin: 16 * root.s
                        anchors.verticalCenter: parent.verticalCenter
                        width: sessionPill.choice ? 16 * root.s : 0; height: 16 * root.s
                        visible: sessionPill.choice
                        name: "updown"; ink: root.fieldText
                    }
                    MouseArea {
                        id: sessionArea
                        anchors.fill: parent
                        enabled: sessionPill.choice
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: menus.toggle("session")
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------ rail
    // Language, keyboard layout, on-screen keyboard and accessibility,
    // standing beside the cards.
    Card {
        id: rail
        theme: root
        x: bento.x + bento.width + bento.gap
        y: bento.y + (bento.height - height) / 2
        width: 56 * root.s
        height: railColumn.implicitHeight + 2 * padding
        padding: 6 * root.s
        radius: width / 2
        delay: 240

        Column {
            id: railColumn
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6 * root.s
            RailButton {
                id: langButton
                theme: root
                icon: "globe"; caption: root.languageCode()
                tip: root.tr("Language")
                open: menus.open === "language"
                onActivated: menus.toggle("language")
            }
            RailButton {
                id: keyButton
                theme: root
                visible: typeof keyboard !== "undefined" && keyboard.layouts && keyboard.layouts.length > 0
                icon: "keyboard"
                caption: visible && keyboard.layouts[keyboard.currentLayout] ? String(keyboard.layouts[keyboard.currentLayout].shortName).toUpperCase() : ""
                tip: root.tr("Keyboard")
                open: menus.open === "keyboard"
                onActivated: menus.toggle("keyboard")
            }
            RailButton {
                theme: root
                visible: osk.available
                icon: "osk"
                tip: root.tr("On-screen keyboard")
                active: osk.shown
                onActivated: { menus.open = ""; osk.shown = !osk.shown; password.forceActiveFocus() }
            }
            RailButton {
                id: accessButton
                theme: root
                icon: "access"
                tip: root.tr("Accessibility")
                active: root.largeText || root.contrast
                open: menus.open === "access"
                onActivated: menus.toggle("access")
            }
        }
    }

    // ------------------------------------------------------------ menus
    Item {
        id: menus
        property string open: ""
        function toggle(name) { open = open === name ? "" : name }
        anchors.fill: parent
        z: 10

        // Session names (only Eduka-Desktop is normally listed).
        Item {
            id: sessionNames
            property var names: []
            Repeater {
                model: sessionModel
                delegate: Item {
                    Component.onCompleted: {
                        var n = sessionNames.names.slice(); n[index] = model.name; sessionNames.names = n
                    }
                }
            }
        }

        PopupMenu {
            theme: root
            visible: menus.open === "user"
            anchorItem: userBox; side: "below"; minWidth: userBox.width
            items: {
                var m = root.userList.map(function(u, i) {
                    return { text: u.real.length > 0 ? u.real : u.name, sub: u.real.length > 0 && u.real !== u.name ? u.name : "",
                             checked: !root.manualUser && i === root.userIndex, icon: "user" }
                })
                m.push({ text: root.tr("Other user…"), icon: "plus" })
                return m
            }
            onPicked: function(i) {
                menus.open = ""
                if (i < root.userList.length) root.chooseUser(i)
                else root.otherUser()
            }
        }
        PopupMenu {
            theme: root
            visible: menus.open === "session"
            anchorItem: sessionPill; side: "below"; minWidth: sessionPill.width
            title: root.tr("Session")
            items: sessionNames.names.map(function(n, i) { return { text: n, checked: i === root.sessionIndex } })
            onPicked: function(i) { root.sessionIndex = i; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root
            visible: menus.open === "language"
            anchorItem: langButton; side: "left"
            title: root.tr("Language")
            note: root.tr("Used on this screen and on the desktop after you sign in.")
            items: root.languages.map(function(l) { return { text: l.code === "" ? root.tr("System language") : l.name, checked: l.code === root.language } })
            onPicked: function(i) { root.language = root.languages[i].code; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root
            visible: menus.open === "keyboard"
            anchorItem: keyButton; side: "left"
            title: root.tr("Keyboard")
            items: {
                var m = []
                if (!keyButton.visible) return m
                for (var i = 0; i < keyboard.layouts.length; i++) {
                    var l = keyboard.layouts[i]
                    m.push({ text: l.longName, sub: String(l.shortName).toUpperCase(), checked: i === keyboard.currentLayout })
                }
                return m
            }
            onPicked: function(i) { keyboard.currentLayout = i; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root
            visible: menus.open === "access"
            anchorItem: accessButton; side: "left"
            title: root.tr("Accessibility")
            items: [
                { text: root.tr("Larger text"), checked: root.largeText },
                { text: root.tr("High contrast"), checked: root.contrast },
                { text: root.tr("On-screen keyboard") + (osk.available ? "" : " — " + root.tr("Not installed")), checked: osk.shown, enabled: osk.available }
            ]
            onPicked: function(i) {
                if (i === 0) root.largeText = !root.largeText
                else if (i === 1) root.contrast = !root.contrast
                else { osk.shown = !osk.shown; menus.open = "" }
                password.forceActiveFocus()
            }
        }
    }

    // ------------------------------------------------------------ on-screen keyboard
    // Qt Virtual Keyboard is optional: when its QML module is missing the
    // loader fails quietly and the rail and the menu say so.
    Loader {
        id: osk
        property bool shown: false
        property bool available: status === Loader.Ready
        source: "VirtualKeyboard.qml"
        anchors.left: parent.left; anchors.right: parent.right
        y: shown ? parent.height - height : parent.height
        z: 20
        visible: shown && available
        Behavior on y { NumberAnimation { duration: 160 } }
    }

    Keys.onEscapePressed: menus.open = ""

    Component.onCompleted: {
        loadLanguage()
        loadFingerprint()
        Qt.callLater(function() {
            pickInitialUser()
            if (root.manualUser && userField.text.length === 0) userField.forceActiveFocus()
            else password.forceActiveFocus()
        })
    }
}
