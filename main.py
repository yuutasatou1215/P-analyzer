import flet as ft
import flet.canvas as cv
import random
import os
import warnings
import math

warnings.filterwarnings("ignore", category=DeprecationWarning)

def main(page: ft.Page):
    # --- #セクション1：基本設定 & 内部状態 ---
    page.title = "PSGt v7.37.16 Alpha" 
    page.bgcolor = "black" 
    page.padding, page.spacing = 0, 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    state = {
        "hit_sequences": [{"top_v": 0, "spin": 0, "ren": 0, "type": "top", "is_jitan": False, "diff": 0}], 
        "current_payout": 0, 
        "is_complete": False,
        "total_hit": 0,
        "first_hit": 0,
        "rush_entries": 0,
        "current_spin": 0,
        "total_spin": 0
    }

    # スナックバーの新しい定義方法（エラー回避用）
    def show_snack(message):
        page.snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar.open = True
        page.update()

    # --- #セクション2：Sレイヤー（設定項目） ---
    初当確率_in = ft.TextField(label="初当確率", value="319.7", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    突入率_in = ft.TextField(label="突入率%", value="50", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    右打確率_in = ft.TextField(label="右打確率", value="99.4", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    ST回数_in = ft.TextField(label="ST回数", value="163", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    時短回数_in = ft.TextField(label="時短回数", value="100", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    回転率_in = ft.TextField(label="回転率", value="17.0", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    ヘソ賞球_in = ft.TextField(label="ヘソ賞球", value="1", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    電サポ賞球_in = ft.TextField(label="電サポ賞球", value="1", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    アタッカー_in = ft.TextField(label="アタッカー", value="15", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    カウント_in = ft.TextField(label="カウント", value="10", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    初当玉数_in = ft.TextField(label="初当玉数", value="450", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    ベース_in = ft.TextField(label="ベース", value="3.0", width=110, height=45, text_size=10, bgcolor="transparent", color="white", border_color="white", label_style=ft.TextStyle(color="white70"), content_padding=10)
    
    振分_input = ft.TextField(label="右打振分 (玉数:%)", value="1500:100", width=345, height=45, text_size=11, color="white", border_color="white", label_style=ft.TextStyle(color="white"))
    賞球_input = ft.TextField(label="賞球表", value="準備中ｗ", width=345, height=45, text_size=11, color="white", border_color="white", label_style=ft.TextStyle(color="white"))

    # --- #セクション3：Gレイヤー ---
    graph_canvas = cv.Canvas(height=240)
    history_row = ft.Row(spacing=0, vertical_alignment="end")
    history_container = ft.Container(content=history_row, padding=ft.padding.only(top=240, bottom=20))
    scale_left = ft.Container(content=ft.Stack([]), width=40, height=240)
    
    graph_scroll_area = ft.Row(
        controls=[ft.Stack([graph_canvas, history_container], width=390)], 
        scroll=ft.ScrollMode.HIDDEN, 
        height=380,
        width=360
    )
    
    def on_slider_change(e):
        page.run_task(graph_scroll_area.scroll_to, offset=float(e.control.value), duration=0)
        page.update()

    graph_slider = ft.Slider(min=0, max=100, value=0, on_change=on_slider_change, active_color="cyan", width=360)

    # --- #セクション4：内部計算ロジック部分 ---
    def run_sim(val):
        if state["is_complete"]: return
        try:
            p_list, w_list = [], []
            for p in 振分_input.value.replace(" ", "").split(","):
                item = p.split(":"); p_list.append(int(item[0])); w_list.append(float(item[1]))
            
            bp, rp, st, jl, kr, bv, at, tr = float(初当確率_in.value), float(右打確率_in.value), float(ST回数_in.value), int(時短回数_in.value), float(回転率_in.value), float(ベース_in.value), int(初当玉数_in.value), float(突入率_in.value) / 100
            calc_rush_rate = 1 - math.pow(1 - (1 / rp), st)

            for _ in range(int(val)):
                if state["is_complete"]: break
                h = 0; prob = 1 / bp
                while random.random() > prob: h += 1
                start_payout = state["current_payout"]
                state["current_payout"] -= int(h * ((250 / kr) - (bv * 0.15)))
                state["current_payout"] += int(at * 0.93)
                ren = 1; state["first_hit"] += 1; state["total_hit"] += 1; state["total_spin"] += h
                in_rush = (random.random() < tr) or (h <= jl)
                if in_rush:
                    state["rush_entries"] += 1
                    while random.random() < calc_rush_rate:
                        ren += 1; state["total_hit"] += 1
                        state["current_payout"] += int(random.choices(p_list, weights=w_list)[0] * 0.93)
                        if state["current_payout"] >= 95000: state["is_complete"] = True; break
                state["hit_sequences"].append({"top_v": state["current_payout"], "spin": h, "ren": ren, "is_jitan": h <= jl and ren == 1, "diff": state["current_payout"] - start_payout})
            
            draw_all()
            graph_slider.value = graph_slider.max
            page.run_task(graph_scroll_area.scroll_to, offset=graph_slider.max, duration=0)
            page.update()
        except: pass

    def on_bar_click(spin, ren, is_jitan, diff):
        type_str = "時短引戻" if is_jitan and ren > 1 else ("時短" if is_jitan else ("RUSH" if ren > 1 else "通常"))
        txt_detail.value = f"詳細: {spin}回 / {ren}連 ({type_str}) [増減: {diff:+}]"; page.update()

    image_state = {"files": [], "current_index": 0}
    def update_image_list():
        try:
            if os.path.exists("assets"):
                files = os.listdir("assets")
                # 修正後: 'congrat.png' を除外。1行を4行に展開してロジック追加。
                # 修正前: image_state["files"] = sorted([f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))])
                image_state["files"] = sorted([
                    f for f in files 
                    if f.lower().endswith((".jpg", ".jpeg", ".png")) 
                    and f.lower() != "congrat.png"
                ])
        except: pass
    update_image_list()

    def change_bg(e):
        update_image_list()
        if not image_state["files"]: return
        image_state["current_index"] = (image_state["current_index"] + 1) % len(image_state["files"])
        bg_image.src = f"/{image_state['files'][image_state['current_index']]}"; page.update()

    def reset_simulation(e):
        graph_slider.value = 0; graph_slider.max = 1
        state.update({"hit_sequences": [{"top_v": 0, "spin": 0, "ren": 0, "type": "top", "is_jitan": False, "diff": 0}], "current_payout": 0, "total_hit": 0, "first_hit": 0, "rush_entries": 0, "current_spin": 0, "total_spin": 0, "is_complete": False})
        congrat_image.visible = False
        btn_exe.disabled = btn_10.disabled = btn_100.disabled = btn_start.disabled = False
        txt_payout.value = "+0"; txt_payout.color = "#69F0AE"; edit_current_spin.value = "準備中ｗ"; txt_detail.value = "統計をリセットしました"; draw_all()

    def draw_all():
        seqs = state["hit_sequences"]
        UNIT_W = 40
        total_w = len(seqs) * UNIT_W 
        graph_slider.max = max(0, total_w - 390)
        graph_canvas.width = total_w
        graph_scroll_area.controls[0].width = total_w
        graph_canvas.shapes.clear(); history_row.controls.clear(); scale_left.content.controls.clear()
        
        all_vals = [s["top_v"] for s in seqs]; mx = max(30000, max(all_vals) + 5000); mn = -10000; rng = mx - mn
        def get_y(v): return (mx - max(v, mn)) / rng * 240
        for v in range(-10000, int(mx)+10000, 10000):
            y_pos = get_y(v)
            graph_canvas.shapes.append(cv.Line(0, y_pos, total_w, y_pos, ft.Paint(color="cyan" if v == 0 else "white10", stroke_width=1)))
            scale_left.content.controls.append(ft.Text(f"{v//1000}k", style=ft.TextStyle(size=9, color="white54"), top=y_pos-7, left=2))
        
        prev_x, prev_y = 0, get_y(0)
        for i, curr in enumerate(seqs):
            if i == 0: continue
            curr_x, curr_y = i * UNIT_W, get_y(curr["top_v"])
            graph_canvas.shapes.append(cv.Line(prev_x, prev_y, curr_x, curr_y, ft.Paint(color="#69F0AE", stroke_width=2)))
            color_bar = "#42A5F5" if curr["is_jitan"] else ("#FF9800" if curr["ren"] > 1 else "#D32F2F")
            history_row.controls.append(ft.Container(content=ft.Column([ft.Text(str(curr["spin"]), size=9, color="white70"), ft.Container(height=min(curr["spin"]//12, 90), width=24, bgcolor=color_bar, border_radius=2), ft.Text(f"{curr['ren']}連", size=10, color="white")], horizontal_alignment="center", spacing=1, alignment="end"), width=UNIT_W, height=140, ink=True, on_click=lambda e, s=curr["spin"], r=curr["ren"], j=curr["is_jitan"], d=curr["diff"]: on_bar_click(s, r, j, d)))
            prev_x, prev_y = curr_x, curr_y
            
        txt_payout.value = f"{state['current_payout']:+,}"; txt_payout.color = "#69F0AE" if state["current_payout"] >= 0 else "#FF5252"; congrat_image.visible = state["is_complete"]
        if state["first_hit"] > 0:
            avg_hit = state["total_spin"] / state["first_hit"]; cont_rate = (1 - (state["first_hit"] / state["total_hit"])) * 100; entry_rate = (state["rush_entries"] / state["first_hit"]) * 100
            stat_panel.content.content.controls[1].value = f"実質初当り確率: 1/{avg_hit:.1f}"; stat_panel.content.content.controls[1].color = "yellow"
            stat_panel.content.content.controls[2].value = f"実質継続率: {cont_rate:.1f}%"; stat_panel.content.content.controls[2].color = "yellow"
            stat_panel.content.content.controls[3].value = f"実質突入率: {entry_rate:.1f}%"; stat_panel.content.content.controls[3].color = "yellow"
        stat_panel.content.content.controls[0].value = f"総当: {state['total_hit']} / 初当: {state['first_hit']}"; page.update()

    # --- #セクション5：Sレイヤー（詳細設定パネル） ---
    def toggle_settings(open_state): 
        settings_layer.top = 0 if open_state else -2000
        settings_layer.update()

    def CustomBtn(t, c, f, ex=False): return ft.Container(content=ft.Text(t, color="white", weight="bold"), bgcolor=c, padding=10, border_radius=8, on_click=f, expand=ex, alignment=ft.Alignment(0, 0))

    input_rows = []
    keys = [初当確率_in, 突入率_in, 右打確率_in, ST回数_in, 時短回数_in, 回転率_in, ヘソ賞球_in, 電サポ賞球_in, アタッカー_in, カウント_in, 初当玉数_in, ベース_in]
    for i in range(0, 12, 3): input_rows.append(ft.Row(keys[i:i+3], alignment="center", spacing=5))
    input_rows.extend([ft.Row([振分_input], alignment="center"), ft.Row([賞球_input], alignment="center")])

    settings_layer = ft.Container(content=ft.Column([ft.Text("PSGt 機種詳細設定", size=22, weight="bold"), ft.Text("HAL Project Team", size=12, color="white54"), ft.Container(height=400, content=ft.Column(input_rows, scroll="auto")), CustomBtn("背景切替", "bluegrey800", change_bg), ft.ElevatedButton("閉じる", on_click=lambda _: toggle_settings(False))], horizontal_alignment="center", spacing=15), bgcolor="#BB000000", padding=20, width=390, height=844, left=0, top=-2000, animate_position=600)

    # --- UI本体レイアウト ---
    bg_image = ft.Image(src="/bg_abstract.jpg", opacity=0.4, fit="cover", width=390, height=844) if image_state["files"] else ft.Container(bgcolor="#1A1A1A", width=390, height=844)
    stat_panel = ft.TransparentPointer(content=ft.Container(content=ft.Column([ft.Text(f"総当: 0 / 初当: 0", size=11, color="white", weight="bold"), ft.Text("実質初当確率: -", size=10, color="yellow"), ft.Text("実質継続率: -", size=10, color="yellow"), ft.Text("実質突入率: -", size=10, color="yellow")], spacing=2, tight=True), padding=10, bgcolor="#4D000000", border_radius=5, width=160))
    congrat_image = ft.Image(src="congrat.png", width=350, height=200, fit="contain", visible=False)
    graph_container = ft.Stack([graph_scroll_area, ft.TransparentPointer(scale_left, left=0, top=0), stat_panel, ft.TransparentPointer(content=ft.Container(content=congrat_image, alignment=ft.Alignment(0, 0)))], height=380)

    txt_payout = ft.Text("+0", color="#69F0AE", size=32, weight="bold", italic=True)
    edit_current_spin = ft.TextField(value="準備中ｗ", width=120, height=40, text_size=16, color="white70", bgcolor="transparent", border="none", read_only=True)
    display_stats_row = ft.Row([ft.Container(txt_payout, alignment=ft.Alignment(1, 0), expand=1), ft.Container(edit_current_spin, alignment=ft.Alignment(-1, 0), expand=1)], spacing=20)
    txt_detail = ft.Text("履歴をタップして詳細を表示", color="white", size=13)
    detail_container = ft.Container(txt_detail, padding=6, bgcolor="white10", border_radius=8, margin=ft.Margin(15, 0, 15, 2), alignment=ft.Alignment(0, 0))

    btn_10 = CustomBtn("▶ 10 回", "bluegrey800", lambda _: run_sim(10), True)
    btn_100 = CustomBtn("▶ 100 回", "bluegrey900", lambda _: run_sim(100), True)
    n_hit_input = ft.TextField(value="1", width=50, height=35, text_size=12, text_align="center", color="white", border_color="white")
    btn_exe = CustomBtn("実行", "indigo700", lambda e: run_sim(n_hit_input.value))
    
    # 修正：STARTボタンのイベントハンドラ
    btn_start = ft.Container(ft.Text("START", color="white", weight="bold"), bgcolor="blue700", padding=10, border_radius=8, on_click=lambda _: show_snack("リアルタイムモードは準備中ｗ"), width=80, alignment=ft.Alignment(0, 0))

    main_ui = ft.Container(content=ft.Column([ft.Row([ft.Text("PSGt v7.37.16 Alpha", color="cyan", weight="bold"), ft.IconButton(ft.Icons.SETTINGS, icon_size=20, on_click=lambda _: toggle_settings(True))], alignment="spaceBetween"), graph_container, ft.Container(graph_slider, padding=ft.padding.only(left=15, right=15)), detail_container, display_stats_row, ft.Column([ft.Row([btn_10, btn_100]), ft.Row([btn_start, ft.Row([ft.Text("初当り", color="white"), n_hit_input, ft.Text("回", color="white")], spacing=5), btn_exe, ft.IconButton(ft.Icons.REFRESH, on_click=reset_simulation, icon_color="red")], alignment="center")], spacing=5)], width=360, spacing=0), alignment=ft.Alignment(0, -1), padding=10)

    page.add(ft.Stack([bg_image, main_ui, settings_layer], width=390, height=844))
    draw_all()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")