from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess, time, os, json
ROOT=Path(__file__).parent
PORT=4186
server=subprocess.Popen(['python','-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 time.sleep(.8)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1600,'height':930},device_scale_factor=1)
  page.set_default_timeout(6000)
  errors=[]
  page.on('pageerror',lambda err:errors.append(str(err)))
  html=(ROOT/'index.html').read_text().replace('<link rel="stylesheet" href="./styles.css" />','<style>'+ (ROOT/'styles.css').read_text() + '</style>').replace('<script src="./scene.js" defer></script>','').replace('<script src="./app.js" defer></script>','')
  page.set_content(html,wait_until='domcontentloaded')
  page.add_script_tag(content=(ROOT/'scene.js').read_text())
  page.add_script_tag(content=(ROOT/'app.js').read_text())
  page.wait_for_timeout(1500)
  print('webgl',page.evaluate('window.breakthroughDebug.getWebGL()'))
  print('errors after initial load',errors)
  page.screenshot(path='/mnt/data/breakthrough_initial.png',full_page=True)
  assert page.get_by_text('Готов оживить свою первую машину?').is_visible()
  page.get_by_role('button',name='Поехали!').click()
  print('step1',page.evaluate('window.breakthroughDebug.getState().step'))
  page.get_by_role('button',name='Открыть кран',exact=True).click()
  page.wait_for_timeout(2300)
  print('flow amounts',page.evaluate('({bottle:window.breakthroughDebug.getState().bottle,tank:window.breakthroughDebug.getState().tank,valve:window.breakthroughDebug.getState().valve})'))
  assert page.evaluate('window.breakthroughDebug.getState().observedOpen') is True
  page.screenshot(path='/mnt/data/breakthrough_water_flow.png',full_page=True)
  page.get_by_role('button',name='Узнать, почему вода течёт').click()
  page.get_by_role('button',name='Показать путь воды').click()
  page.get_by_role('button',name='Провести свой эксперимент').click()
  page.locator('#valveSlider').fill('50')
  page.wait_for_timeout(1800)
  assert page.evaluate('window.breakthroughDebug.getState().halfObserved') is True
  page.screenshot(path='/mnt/data/breakthrough_experiment.png',full_page=True)
  page.get_by_role('button',name='Проверить свою догадку').click()
  page.get_by_role('button',name='Вода потечёт быстрее').click()
  page.get_by_role('button',name='Проверить догадку').click()
  assert page.evaluate('window.breakthroughDebug.getState().predictionChecked')
  page.get_by_role('button',name='Теперь соберу сам!').click()
  print('step5',page.evaluate('window.breakthroughDebug.getState().step'))
  page.screenshot(path='/mnt/data/breakthrough_builder.png',full_page=True)
  for part,slot in [('Бак с водой','ОТКУДА ВОДА?'),('Трубка','КУДА ОНА ИДЁТ?'),('Кран','КТО УПРАВЛЯЕТ?'),('Бутылка','КУДА НАЛИВАЕМ?')]:
   page.locator('[data-part='+{'Бак с водой':'tank','Трубка':'pipe','Кран':'valve','Бутылка':'bottle'}[part]+']').click()
   page.locator('[data-slot='+{'ОТКУДА ВОДА?':'tank','КУДА ОНА ИДЁТ?':'pipe','КТО УПРАВЛЯЕТ?':'valve','КУДА НАЛИВАЕМ?':'bottle'}[slot]+']').click()
  print('parts',page.evaluate('window.breakthroughDebug.getState().parts'))
  page.get_by_role('button',name='Запустить мою установку').click()
  page.wait_for_timeout(2400)
  print('build complete',page.evaluate('window.breakthroughDebug.getState().buildComplete'))
  assert page.evaluate('window.breakthroughDebug.getState().buildComplete')
  page.get_by_role('button',name='Получить первое достижение').click()
  print('step end',page.evaluate('window.breakthroughDebug.getState().step'))
  page.screenshot(path='/mnt/data/breakthrough_complete.png',full_page=True)
  page.reload(wait_until='domcontentloaded')
  # About:blank cannot persist document across reload; reload the same inline bundle.
  page.set_content(html,wait_until='domcontentloaded')
  page.add_script_tag(content=(ROOT/'scene.js').read_text())
  page.add_script_tag(content=(ROOT/'app.js').read_text())
  page.wait_for_timeout(500)
  # LocalStorage is not available in an about:blank test context.
  print('reload step',page.evaluate('window.breakthroughDebug.getState().step'))
  print('errors all',errors)
  assert not errors,errors
  mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
  mobile.set_content(html,wait_until='domcontentloaded')
  mobile.add_script_tag(content=(ROOT/'scene.js').read_text())
  mobile.add_script_tag(content=(ROOT/'app.js').read_text())
  mobile.wait_for_timeout(1200)
  print('mobile overflow',mobile.evaluate('document.documentElement.scrollWidth>innerWidth'))
  mobile.screenshot(path='/mnt/data/breakthrough_mobile.png',full_page=True)
  browser.close()
finally:
 server.terminate()