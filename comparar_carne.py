from playwright.sync_api import sync_playwright
import re

# ==========================================
# DEFINICIÓN DE URLs (Globales para la API)
# ==========================================
url_carrefour = "https://www.carrefour.es/supermercado/preparado-de-carne-burger-meat-vacuno-y-cerdo-el-mercado-500-g/R-VC4AECOMM-479496/p"
url_dia = "https://www.dia.es/carnes/hamburguesas-carne-picada-y-albondigas/p/261242" 
url_alcampo = "https://www.compraonline.alcampo.es/products/bandeja-de-preparado-de-carne-picada-mixta-vacuno-cerdo-elaborada-sin-gluten-roler-800-g/76688"
url_alimerka = "https://www.alimerkaonline.es/460103.html"
url_aldi = "https://www.aldi.es/producto/burger-meat-picada-de-vacuno-y-cerdo-601491700.html"
url_mercadona = "https://tienda.mercadona.es/product/3453/preparado-carne-picada-vacuno-cerdo-bandeja"
url_familia = "https://www.familiaonline.es/es/productdetail/23636418-burguer-meat-cerdo-vacuno-o-caurel-bandeja-1-kg/"
url_masymas = "https://www.supermasymasonline.com/carne-picada-mixta-kg/0039513.html"


def limpiar_precio(precio_str):
    try:
        limpio = str(precio_str).replace("€", "").replace(",", ".").strip()
        match = re.search(r'\d+\.\d+|\d+', limpio)
        if match:
            return float(match.group())
        return float(limpio)
    except:
        return 999999.0

def comparar_supermercados(url_carrefour, url_dia, url_alcampo, url_alimerka, url_aldi, url_mercadona, url_familia, url_masymas):
    resultados = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080"
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            locale="es-ES",
            timezone_id="Europe/Madrid",
            bypass_csp=True
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        # ==========================================
        # 1. CARREFOUR
        # ==========================================
        print("\n[Carrefour] Consultando...")
        page_carrefour = context.new_page()
        datos_carrefour = {"super": "Carrefour", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_carrefour.goto(url_carrefour, timeout=60000)
            try:
                page_carrefour.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            datos_carrefour["nombre"] = page_carrefour.locator(".product-header__name").first.inner_text().strip()
            datos_carrefour["actual"] = page_carrefour.locator(".buybox__price").first.inner_text().strip()
            try:
                datos_carrefour["kg"] = page_carrefour.locator(".buybox__price-per-unit").first.inner_text().strip()
            except:
                pass
        except Exception as e:
            print(f"[Aviso Carrefour] {e}")
        resultados.append(datos_carrefour)

        # ==========================================
        # 2. DIA
        # ==========================================
        print("[DIA] Consultando...")
        page_dia = context.new_page()
        datos_dia = {"super": "DIA", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_dia.goto(url_dia, timeout=60000)
            try:
                page_dia.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            page_dia.wait_for_timeout(3000)
            
            try:
                datos_dia["nombre"] = page_dia.locator("h1").first.inner_text().strip()
            except:
                pass
            
            datos_dia["actual"] = page_dia.evaluate("""() => {
                let selectors = ['.price-current', '.sale-price', '[data-test="price"]', '.buy-box__active-price', 'span', 'div'];
                for (let sel of selectors) {
                    let elems = document.querySelectorAll(sel);
                    for (let el of elems) {
                        let text = el.innerText.trim();
                        if (text.includes('€') && text.length < 8 && /\d+[,.]\d+/.test(text)) return text;
                    }
                }
                return 'N/D';
            }""")

            # Extracción precio kg DIA
            try:
                datos_dia["kg"] = page_dia.locator(".buy-box__price-per-unit").first.inner_text().strip()
            except:
                pass

        except Exception as e:
            print(f"[Aviso DIA] {e}")
        resultados.append(datos_dia)

        # ==========================================
        # 3. ALCAMPO
        # ==========================================
        print("[Alcampo] Consultando...")
        page_alcampo = context.new_page()
        datos_alcampo = {"super": "Alcampo", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_alcampo.goto(url_alcampo, timeout=60000)
            try:
                page_alcampo.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            page_alcampo.wait_for_timeout(4000)
            datos_alcampo["nombre"] = page_alcampo.evaluate("() => document.querySelector('h1') ? document.querySelector('h1').innerText.trim() : 'No encontrado'")
            datos_alcampo["actual"] = page_alcampo.evaluate("""() => {
                let main = document.querySelector('main');
                if (!main) return 'N/D';
                for (let el of main.querySelectorAll('span, div')) {
                    let texto = el.innerText.trim();
                    if (texto.includes('€') && texto.length < 10 && !texto.toLowerCase().includes('kg')) {
                        if (/\d+[,.]\d+/.test(texto)) return texto.split('\\n')[0].trim();
                    }
                }
                return 'N/D';
            }""")

            # Extracción precio kg Alcampo basándose en el HTML aportado (salt-vc o size-container)
            try:
                datos_alcampo["kg"] = page_alcampo.evaluate("""() => {
                    let sizeCont = document.querySelector('[data-test="size-container"]');
                    if (sizeCont) return sizeCont.innerText.replace(/\\s+/g, ' ').trim();
                    for (let span of document.querySelectorAll('span')) {
                        let t = span.innerText.trim();
                        if (t.includes('por kilogramo') || t.includes('€/kg')) return t;
                    }
                    return 'N/D';
                }""")
            except:
                pass

        except Exception as e:
            print(f"[Aviso Alcampo] {e}")
        resultados.append(datos_alcampo)

        # ==========================================
        # 4. ALIMERKA
        # ==========================================
        print("\n[Alimerka] Consultando...")

        context_alimerka = browser.new_context(
            locale="es-ES",
            timezone_id="Europe/Madrid",
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )

        page_alimerka = context_alimerka.new_page()

        datos_alimerka = {
            "super": "Alimerka",
            "nombre": "No encontrado",
            "actual": "N/D",
            "anterior": "Sin oferta",
            "kg": "N/D"
        }

        try:
            page_alimerka.goto(
                "https://www.alimerkaonline.es/",
                timeout=60000,
                wait_until="domcontentloaded"
            )
            page_alimerka.wait_for_timeout(3000)

            try:
                page_alimerka.locator("#onetrust-accept-btn-handler").click(timeout=3000)
                page_alimerka.wait_for_timeout(1000)
            except:
                pass

            enlace_invitado = page_alimerka.locator("a.js-open-guest")
            enlace_invitado.wait_for(state="visible", timeout=10000)
            enlace_invitado.click()
            page_alimerka.wait_for_timeout(2000)

            campo_cp = page_alimerka.locator("#zipCode")
            campo_cp.wait_for(state="visible", timeout=10000)
            campo_cp.fill("33201")

            boton_comprobar = page_alimerka.locator("button.js-check-zipcode")
            boton_comprobar.wait_for(state="visible", timeout=10000)
            boton_comprobar.click()
            page_alimerka.wait_for_timeout(5000)

            respuesta = page_alimerka.goto(
                url_alimerka,
                timeout=60000,
                wait_until="domcontentloaded"
            )
            page_alimerka.wait_for_timeout(5000)

            contenido = page_alimerka.locator("body").inner_text()
            es_error = bool(re.search(r"404|página no encontrada|page not found", contenido, re.I))

            if es_error:
                datos_alimerka["nombre"] = "Error al cargar el producto"
            else:
                try:
                    datos_alimerka["nombre"] = page_alimerka.locator("h1").first.inner_text().strip()
                except:
                    pass

                precio = page_alimerka.evaluate("""
                    () => {
                        const selectores = [
                            '.sales .value',
                            '.price__number',
                            '.product-price',
                            '.price',
                            '[class*="price"]'
                        ];

                        for (const selector of selectores) {
                            for (const el of document.querySelectorAll(selector)) {
                                const t = (el.innerText || el.textContent || '').trim();
                                if (
                                    t.length < 20 &&
                                    /\\d+[,.]\\d{2}\\s*€?/.test(t) &&
                                    !/0[,.]00/.test(t)
                                ) {
                                    return t.includes('€') ? t : t + ' €';
                                }
                            }
                        }
                        return null;
                    }
                """)
                if precio:
                    datos_alimerka["actual"] = precio

                # Extracción precio kg Alimerka
                try:
                    kg_alimerka = page_alimerka.evaluate("""() => {
                        let el = document.querySelector('.sales .value, .price .value');
                        if (el) return el.innerText.trim();
                        return 'N/D';
                    }""")
                    if kg_alimerka and kg_alimerka != 'N/D':
                        datos_alimerka["kg"] = kg_alimerka if '€' in kg_alimerka else kg_alimerka + ' €/kg'
                except:
                    pass

        except Exception as e:
            print(f"[Aviso Alimerka] {e}")

        resultados.append(datos_alimerka)
        context_alimerka.close()

        # ==========================================
        # 5. ALDI
        # ==========================================
        print("[Aldi] Consultando...")
        page_aldi = context.new_page()
        datos_aldi = {"super": "Aldi", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_aldi.goto(url_aldi, timeout=60000)
            try:
                page_aldi.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            
            page_aldi.wait_for_timeout(5000)
            
            try:
                datos_aldi["nombre"] = page_aldi.locator("h1").first.inner_text().strip()
            except:
                pass

            datos_aldi["actual"] = page_aldi.evaluate("""() => {
                let el = document.querySelector("[data-testid='product-card-detail-tag-current-price'], .price, .mod-article-header__price-value");
                if (el) {
                    let t = el.innerText.trim();
                    return t.includes('€') ? t : t + ' €';
                }
                let elems = document.querySelectorAll('span, div');
                for (let e of elems) {
                    let t = e.innerText.trim();
                    if (t.includes('€') && t.length < 8 && /\d+[,.]\d+/.test(t)) return t;
                }
                return 'N/D';
            }""")

            # Extracción robusta para Aldi
            try:
                datos_aldi["kg"] = page_aldi.evaluate("""() => {
                    let baseEl = document.querySelector("[data-testid='product-card-detail-tag-base-price']");
                    let unitEl = document.querySelector("[data-testid='product-card-detail-tag-sales-unit']");
                    
                    let textoBase = baseEl ? baseEl.innerText.trim() : '';
                    let textoUnit = unitEl ? unitEl.innerText.trim() : '';
                    
                    if (textoBase) {
                        let match = textoBase.match(/\\d+[,.]\\d+/);
                        if (match) {
                            let valor = match[0];
                            return textoUnit ? `${valor} €/kg (${textoUnit})` : `${valor} €/kg`;
                        }
                    }
                    return 'N/D';
                }""")
            except:
                pass

        except Exception as e:
            print(f"[Aviso Aldi] {e}")
        resultados.append(datos_aldi)

        # ==========================================
        # 6. MERCADONA
        # ==========================================
        print("[Mercadona] Consultando...")
        page_mercadona = context.new_page()
        datos_mercadona = {"super": "Mercadona", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_mercadona.goto(url_mercadona, timeout=60000)
            try:
                page_mercadona.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            
            try:
                input_cp = page_mercadona.locator("input[name='postalCode']")
                if input_cp.count() > 0:
                    input_cp.first.fill("33201")
                    page_mercadona.keyboard.press("Enter")
                    page_mercadona.wait_for_timeout(3000)
            except:
                pass

            page_mercadona.wait_for_timeout(3000)
            datos_mercadona["nombre"] = page_mercadona.locator(".private-product-detail__description").first.inner_text().strip()
            datos_mercadona["actual"] = page_mercadona.locator("[data-testid='product-price']").first.inner_text().strip()

            # Extracción precio kg Mercadona
            try:
                datos_mercadona["kg"] = page_mercadona.locator(".product-format").first.inner_text().strip()
            except:
                pass

        except Exception as e:
            print(f"[Aviso Mercadona] {e}")
        resultados.append(datos_mercadona)

        # ==========================================
        # 7. FAMILIA
        # ==========================================
        print("[Familia] Consultando...")
        page_familia = context.new_page()
        datos_familia = {"super": "Familia", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_familia.goto(url_familia, timeout=90000)
            try:
                page_familia.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            page_familia.wait_for_timeout(8000)
            datos_familia["nombre"] = page_familia.locator(".description-title").first.inner_text().strip()
            datos_familia["actual"] = page_familia.locator(".offer-now").first.inner_text().strip() + " €"

            # Extracción precio kg Familia
            try:
                datos_familia["kg"] = page_familia.locator(".quantity-text").first.inner_text().strip()
            except:
                pass

        except Exception as e:
            print(f"[Aviso Familia] {e}")
        resultados.append(datos_familia)

        # ==========================================
        # 8. MÁS Y MÁS (Actualizado con los nuevos datos)
        # ==========================================
        print("[Más y Más] Consultando...")
        page_masymas = context.new_page()
        datos_masymas = {"super": "Más y Más", "nombre": "No encontrado", "actual": "N/D", "anterior": "Sin oferta", "kg": "N/D"}
        try:
            page_masymas.goto(url_masymas, timeout=60000)
            try:
                page_masymas.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass
            page_masymas.wait_for_timeout(5000)
            
            # Extraer nombre
            try:
                datos_masymas["nombre"] = page_masymas.locator(".product-name, h1").first.inner_text().strip()
            except:
                pass
            
            # Extraer precio actual (Soporta .sales .value y .prices-ud)
            try:
                datos_masymas["actual"] = page_masymas.locator(".sales .value, .price .value, .prices-ud").first.inner_text().strip().split("\n")[0]
            except:
                pass

            # Extraer precio por kilo y equivalencia exacta para Más y Más basándonos en el HTML real
            try:
                datos_masymas["kg"] = page_masymas.evaluate("""() => {
                    let kgEl = document.querySelector('.unit-price-per-unit-details');
                    let eqEl = document.querySelector('.prices-equivalent');
                    
                    let kgText = kgEl ? kgEl.innerText.replace(/\\s+/g, ' ').trim() : '';
                    let eqText = eqEl ? eqEl.innerText.replace(/\\s+/g, ' ').trim() : '';
                    
                    if (kgText) {
                        return eqText ? `${kgText} ${eqText}` : kgText;
                    }
                    
                    // Fallback por si acaso usa conversion-factor
                    let cf = document.querySelector('.conversion-factor');
                    if (cf) return cf.innerText.replace(/\\s+/g, ' ').trim();
                    
                    return 'N/D';
                }""")
            except:
                pass

        except Exception as e:
            print(f"[Aviso Más y Más] {e}")
        resultados.append(datos_masymas)

        # ==========================================
        # 9. ORDENAR RESULTADOS DE MENOR A MAYOR PRECIO
        # ==========================================
        resultados.sort(key=lambda x: limpiar_precio(x["actual"]))

    try:
        browser.close()
    except:
        pass

    return resultados


if __name__ == "__main__":
    comparar_supermercados(url_carrefour, url_dia, url_alcampo, url_alimerka, url_aldi, url_mercadona, url_familia, url_masymas)