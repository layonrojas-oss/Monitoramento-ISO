def render_card_topo(carteira_atual, cart_reuniao, pct_cart_reuniao, qtd_reunioes, cart_indicando, pct_cart_indicando, cart_ativando, pct_cart_ativando, leads_por_contador, leads_criados):
    return f"""<div style="position: relative; background: #ffffff; border-radius: 20px; padding: 35px 20px 20px; box-shadow: 0 12px 30px rgba(0, 51, 102, 0.08); border: 1px solid rgba(0, 51, 102, 0.1); font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin-top: 25px; display: flex; flex-direction: column; height: 100%; min-height: 500px;">
<div style="position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #0056b3, #003366); color: #ffffff; padding: 6px 24px; border-radius: 30px; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; box-shadow: 0 6px 12px rgba(0, 51, 102, 0.3); display: flex; align-items: center; gap: 6px; white-space: nowrap;">🏔️ TOPO</div>
<div style="text-align: center; color: #6c757d; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">TRABALHADO (EC)</div>
<div style="flex-grow: 1; display: flex; flex-direction: column;">
<div style="background: linear-gradient(145deg, #f8f9fa, #e9ecef); padding: 15px 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #003366; box-shadow: inset 0 2px 5px rgba(255,255,255,1), 0 2px 4px rgba(0,0,0,0.02);">
<span style="color: #495057; font-weight: 700; font-size: 12px; letter-spacing: 0.5px;">CARTEIRA ATUAL</span>
<span style="font-size: 24px; font-weight: 900; color: #003366; text-shadow: 1px 1px 0px rgba(255,255,255,0.5);">{int(carteira_atual)}</span>
</div>
<div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 25px;">
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">💼 Com Reunião</span>
<div style="text-align: right;">
<span style="font-weight: 700; color: #212529; font-size: 14px;">{int(cart_reuniao)}</span>
<span style="background: #e3f2fd; color: #0056b3; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 10px; margin-left: 6px;">{pct_cart_reuniao:.0%}</span>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">🤝 Reuniões Feitas</span>
<span style="font-weight: 700; color: #212529; font-size: 14px;">{int(qtd_reunioes)}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">📣 Indicando</span>
<div style="text-align: right;">
<span style="font-weight: 700; color: #212529; font-size: 14px;">{int(cart_indicando)}</span>
<span style="background: #e3f2fd; color: #0056b3; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 10px; margin-left: 6px;">{pct_cart_indicando:.0%}</span>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">🚀 Ativando</span>
<div style="text-align: right;">
<span style="font-weight: 700; color: #212529; font-size: 14px;">{int(cart_ativando)}</span>
<span style="background: #e3f2fd; color: #0056b3; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 10px; margin-left: 6px;">{pct_cart_ativando:.0%}</span>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">📈 Leads / Contador</span>
<span style="font-weight: 700; color: #212529; font-size: 14px;">{leads_por_contador:.1f}</span>
</div>
</div>
</div>
<div style="background: linear-gradient(135deg, #0056b3, #003366); padding: 18px; border-radius: 14px; text-align: center; position: relative; overflow: hidden; box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2); margin-top: auto;">
<div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%); transform: rotate(30deg); pointer-events: none;"></div>
<div style="color: #cce5ff; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; position: relative; z-index: 1;">LEADS CRIADOS</div>
<div style="font-size: 32px; font-weight: 900; color: #ffffff; position: relative; z-index: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{int(leads_criados)}</div>
</div>
</div>"""

def render_card_meio(l_agendados, tx_agend, d_realizadas):
    return f"""<div style="position: relative; background: #ffffff; border-radius: 20px; padding: 35px 20px 20px; box-shadow: 0 12px 30px rgba(253, 126, 20, 0.08); border: 1px solid rgba(253, 126, 20, 0.1); font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin-top: 25px; display: flex; flex-direction: column; height: 100%; min-height: 500px;">
<div style="position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #fd7e14, #d94a00); color: #ffffff; padding: 6px 24px; border-radius: 30px; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; box-shadow: 0 6px 12px rgba(253, 126, 20, 0.3); display: flex; align-items: center; gap: 6px; white-space: nowrap;">🔄 MEIO</div>
<div style="text-align: center; color: #6c757d; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Qualificação (SDR)</div>   
<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; margin-bottom: 25px;">
<div style="background: linear-gradient(145deg, #fff4e6, #ffedd5); padding: 20px; border-radius: 14px; margin-bottom: 30px; text-align: center; border-left: 4px solid #fd7e14; box-shadow: inset 0 2px 5px rgba(255,255,255,1), 0 4px 10px rgba(253, 126, 20, 0.05);">
<div style="color: #d94a00; font-size: 12px; font-weight: 800; letter-spacing: 1px; margin-bottom: 8px;">LEADS AGENDADOS</div>
<div style="font-size: 36px; font-weight: 900; color: #fd7e14; text-shadow: 1px 1px 0px rgba(255,255,255,0.8); line-height: 1;">{int(l_agendados)}</div>
</div>
<div style="text-align: center; position: relative;">
<div style="position: absolute; width: 1px; height: 100%; background: linear-gradient(to bottom, transparent, #ffe8cc, transparent); left: 10px; top: 0;"></div>
<div style="position: absolute; width: 1px; height: 100%; background: linear-gradient(to bottom, transparent, #ffe8cc, transparent); right: 10px; top: 0;"></div>
<div style="font-size: 11px; color: #868e96; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">Taxa de Agendamento</div>
<div style="font-size: 42px; font-weight: 900; background: linear-gradient(135deg, #fd7e14, #d94a00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 8px 0; line-height: 1;">{tx_agend:.0%}</div>
<div style="font-size: 11px; color: #adb5bd; font-weight: 500; background: #f8f9fa; display: inline-block; padding: 4px 12px; border-radius: 20px; border: 1px solid #f1f3f5;">Leads Criados → Agendados</div>
</div>
</div>
<div style="background: linear-gradient(135deg, #fd7e14, #d94a00); padding: 18px; border-radius: 14px; text-align: center; position: relative; overflow: hidden; box-shadow: 0 8px 16px rgba(253, 126, 20, 0.25); margin-top: auto;">
<div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%); transform: rotate(30deg); pointer-events: none;"></div>
<div style="color: #ffe8cc; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; position: relative; z-index: 1;">DEMOS REALIZADAS</div>
<div style="font-size: 32px; font-weight: 900; color: #ffffff; position: relative; z-index: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{int(d_realizadas)}</div>
</div>
</div>"""

def render_card_fundo(l_conquistados, tx_conv_demos, a_ativados, mult_cnpj, tk_medio, nmrr_bpo, nmrr_sem_bpo, nmrr_total, formatar_moeda):
    return f"""<div style="position: relative; background: #ffffff; border-radius: 20px; padding: 35px 20px 20px; box-shadow: 0 12px 30px rgba(25, 135, 84, 0.08); border: 1px solid rgba(25, 135, 84, 0.1); font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin-top: 25px; display: flex; flex-direction: column; height: 100%; min-height: 500px;">
<div style="position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #20c997, #198754); color: #ffffff; padding: 6px 24px; border-radius: 30px; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; box-shadow: 0 6px 12px rgba(25, 135, 84, 0.3); display: flex; align-items: center; gap: 6px; white-space: nowrap;">💰 FUNDO</div>
<div style="text-align: center; color: #6c757d; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Fechamento (EV)</div>
<div style="flex-grow: 1; display: flex; flex-direction: column;">
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
<div style="background: linear-gradient(145deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 12px; text-align: center; border-bottom: 3px solid #6c757d; box-shadow: inset 0 2px 5px rgba(255,255,255,1), 0 2px 4px rgba(0,0,0,0.02);">
<div style="color: #6c757d; font-size: 10px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px;">LEADS CONQUISTADOS</div>
<div style="font-size: 26px; font-weight: 900; color: #343a40; line-height: 1;">{int(l_conquistados)}</div>
</div>
<div style="background: linear-gradient(145deg, #f0fdf4, #dcfce7); padding: 15px; border-radius: 12px; text-align: center; border-bottom: 3px solid #198754; box-shadow: inset 0 2px 5px rgba(255,255,255,1), 0 2px 4px rgba(25, 135, 84, 0.05);">
<div style="color: #198754; font-size: 10px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px;">TX. CONVERSÃO</div>
<div style="font-size: 26px; font-weight: 900; color: #198754; line-height: 1;">{tx_conv_demos:.0%}</div>
</div>
</div>
<div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 25px;">
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">⚙️ Apps Ativados</span>
<span style="font-weight: 700; color: #212529; font-size: 14px;">{int(a_ativados)}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">🏢 Múltiplos CNPJs</span>
<span style="font-weight: 700; color: #212529; font-size: 14px;">{mult_cnpj:.2f}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">🏷️ Ticket Médio</span>
<span style="font-weight: 800; color: #198754; font-size: 14px; background: #e8f5e9; padding: 2px 8px; border-radius: 6px;">{formatar_moeda(tk_medio)}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: #fdfdfe; padding: 10px 15px; border-radius: 8px; border: 1px solid #f1f3f5; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
<span style="color: #495057; font-size: 13px; font-weight: 500;">📦 FULL / BPO</span>
<div style="display: flex; align-items: center; gap: 6px;">
<span style="font-weight: 700; color: #212529; font-size: 12px;">{formatar_moeda(nmrr_sem_bpo)}</span>
<span style="color: #adb5bd; font-size: 10px;">/</span>
<span style="font-weight: 700; color: #6c757d; font-size: 12px;">{formatar_moeda(nmrr_bpo)}</span>
</div>
</div>
</div>
</div>
<div style="background: linear-gradient(135deg, #20c997, #198754); padding: 18px; border-radius: 14px; text-align: center; position: relative; overflow: hidden; box-shadow: 0 8px 16px rgba(25, 135, 84, 0.25); margin-top: auto;">
<div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%); transform: rotate(30deg); pointer-events: none;"></div>
<div style="color: #d1e7dd; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; position: relative; z-index: 1;">NMRR TOTAL</div>
<div style="font-size: 32px; font-weight: 900; color: #ffffff; position: relative; z-index: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{formatar_moeda(nmrr_total)}</div>
</div>
</div>"""
