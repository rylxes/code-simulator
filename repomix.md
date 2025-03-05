This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix. The content has been processed where comments have been removed, line numbers have been added.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: *.test.ts, *.sh, .idea, .github, .gitignore, repomix.*, **/*.md, dist, src/codesimulator/resources/code, src/codesimulator/back, build, tests
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Line numbers have been added to the beginning of each line

## Additional Info

# Directory Structure
```
src/
  codesimulator/
    resources/
      applications.json
      config.json
      README
    __main__.py
    actions.py
    app_switcher.py
    app.py
    config.py
    key_handler.py
    language_formatter.py
    logging_config.py
    mouse.py
    path_utils.py
  codesimulator.dist-info/
    INSTALLER
    METADATA
    top_level.txt
    WHEEL
CHANGELOG
LICENSE
pyproject.toml
README.rst
```

# Files

## File: src/codesimulator/resources/applications.json
```json
 1: {
 2:   "darwin": {
 3:     "applications": [
 4:       {
 5:         "name": "Google Chrome",
 6:         "process_name": "Google Chrome",
 7:         "bundle_id": "com.google.Chrome"
 8:       },
 9:       {
10:         "name": "IntelliJ IDEA",
11:         "process_name": "IntelliJ IDEA",
12:         "bundle_id": "com.jetbrains.intellij"
13:       },
14:       {
15:         "name": "Sublime Text",
16:         "process_name": "Sublime Text",
17:         "bundle_id": "com.sublimetext.4"
18:       }
19:     ]
20:   },
21:   "win32": {
22:     "applications": [
23:       {
24:         "name": "Google Chrome",
25:         "process_name": "chrome.exe",
26:         "window_class": "Chrome_WidgetWin_1"
27:       },
28:       {
29:         "name": "IntelliJ IDEA",
30:         "process_name": "idea64.exe",
31:         "window_class": "SunAwtFrame"
32:       },
33:       {
34:         "name": "Sublime Text",
35:         "process_name": "sublime_text.exe",
36:         "window_class": "PX_WINDOW_CLASS"
37:       }
38:     ]
39:   },
40:   "linux": {
41:     "applications": [
42:       {
43:         "name": "Google Chrome",
44:         "process_name": "chrome",
45:         "window_class": "Google-chrome"
46:       },
47:       {
48:         "name": "IntelliJ IDEA",
49:         "process_name": "idea.sh",
50:         "window_class": "jetbrains-idea"
51:       },
52:       {
53:         "name": "Sublime Text",
54:         "process_name": "sublime_text",
55:         "window_class": "sublime_text"
56:       }
57:     ]
58:   }
59: }
```

## File: src/codesimulator/resources/config.json
```json
 1: {
 2:     "code": {
 3:         "language": "php",
 4:         "indent_size": 2,
 5:         "max_line_length": 80
 6:     },
 7:     "typing_speed": {
 8:         "min": 0.15,
 9:         "max": 0.25,
10:         "line_break": [0.5, 1.0],
11:         "mistake_rate": 0.09
12:     }
13: }
```

## File: src/codesimulator/resources/README
```
1: Put any application resources (e.g., icons and resources) here;
2: they can be referenced in code as "resources/filename".
```

## File: src/codesimulator/__main__.py
```python
1: from codesimulator.app import main
2: 
3: if __name__ == "__main__":
4:     main().main_loop()
```

## File: src/codesimulator/actions.py
```python
  1: import asyncio
  2: import os
  3: import random
  4: import time
  5: import sys
  6: import json
  7: from typing import Optional
  8: 
  9: import pyautogui
 10: 
 11: from .app_switcher import AppSwitcher
 12: from .config import AppConfig
 13: from .language_formatter import FormatterFactory
 14: from .logging_config import logger
 15: from .mouse import MouseController
 16: 
 17: 
 18: class ActionSimulator:
 19: 
 20: 
 21:     def __init__(self, text_box, app=None):
 22:         self.text_box = text_box
 23:         self.app = app
 24:         self.loop_flag = False
 25:         self._configure_pyautogui()
 26:         self.app_config = AppConfig(app)
 27:         self.app_switcher = AppSwitcher(self.app_config)
 28:         self.formatter_factory = FormatterFactory()
 29:         self.formatter = None
 30:         self.mouse_controller = MouseController()
 31:         self.simulation_mode = "Hybrid"
 32: 
 33:         self.config = self._load_config()
 34:         self._setup_from_config()
 35: 
 36: 
 37:         self.code_files = self._get_code_files()
 38:         self.current_code_index = 0
 39: 
 40:         self.original_indentations = {}
 41: 
 42:     def _setup_from_config(self):
 43:         try:
 44:             code_config = self.config.get('code', {})
 45:             self.language = code_config.get('language', 'python')
 46:             self.indent_size = code_config.get('indent_size', 4)
 47:             self.max_line_length = code_config.get('max_line_length', 80)
 48:             typing_config = self.config.get('typing_speed', {})
 49:             self.typing_speed = {
 50:                 'min': typing_config.get('min', 0.03),
 51:                 'max': typing_config.get('max', 0.07),
 52:                 'line_break': tuple(typing_config.get('line_break', [0.5, 1.0])),
 53:                 'mistake_rate': typing_config.get('mistake_rate', 0.07)
 54:             }
 55:             logger.info("Successfully configured simulation settings")
 56:         except Exception as e:
 57:             logger.error(f"Error setting up configuration: {e}")
 58:             self._setup_default_config()
 59: 
 60:     def _setup_default_config(self):
 61:         logger.warning("Using default configuration settings")
 62:         self.language = 'python'
 63:         self.indent_size = 4
 64:         self.max_line_length = 80
 65:         self.typing_speed = {
 66:             'min': 0.03,
 67:             'max': 0.07,
 68:             'line_break': (0.5, 1.0),
 69:             'mistake_rate': 0.07,
 70:         }
 71: 
 72:     def _get_config_path(self) -> str:
 73:         from .path_utils import get_resource_path
 74:         config_path = get_resource_path(self.app, 'config.json')
 75:         if not os.path.exists(config_path):
 76:             logger.error(f"Config file not found at {config_path}")
 77:             raise FileNotFoundError(f"Config file not found at {config_path}")
 78:         return config_path
 79: 
 80:     def _get_code_files(self) -> list:
 81: 
 82:         from .path_utils import get_resource_path
 83:         code_dir = get_resource_path(self.app, 'code')
 84:         if os.path.isdir(code_dir):
 85:             files = [os.path.join(code_dir, f) for f in os.listdir(code_dir) if f.endswith(".txt")]
 86:             if not files:
 87:                 logger.warning(f"No .txt files found in {code_dir}")
 88:             return files
 89:         else:
 90:             logger.warning(f"Code directory not found: {code_dir}")
 91:             return []
 92: 
 93:     def _load_config(self) -> dict:
 94:         try:
 95:             with open(self._get_config_path(), 'r') as f:
 96:                 config = json.load(f)
 97:                 logger.info("Successfully loaded configuration")
 98:                 return config
 99:         except Exception as e:
100:             logger.error(f"Error loading config: {e}")
101:             raise
102: 
103:     def load_config(self):
104:         try:
105:             config_path = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')
106:             logger.info(f"Loading config from: {config_path}")
107:             with open(config_path, "r") as f:
108:                 config = json.load(f)
109:                 code_config = config.get('code', {})
110:                 self.language = code_config.get("language", "unknown")
111:                 self.indent_size = code_config.get("indent_size", 4)
112:                 self.max_line_length = code_config.get("max_line_length", 80)
113:         except Exception as e:
114:             logger.error(f"Error loading config: {e}")
115:             self.language = "unknown"
116:             self.indent_size = 4
117:             self.max_line_length = 80
118: 
119:     async def simulate_command_tab(self):
120: 
121:         try:
122:             if sys.platform == 'darwin':
123:                 pyautogui.hotkey('command', 'tab')
124:             elif sys.platform == 'win32':
125:                 pyautogui.hotkey('alt', 'tab')
126:             else:
127:                 pyautogui.hotkey('alt', 'tab')
128: 
129:             logger.info("Pressed Command+Tab / Alt+Tab")
130:             await asyncio.sleep(0.5)
131:         except Exception as e:
132:             logger.error(f"Error simulating Command+Tab: {e}")
133: 
134:     def _configure_pyautogui(self):
135:         try:
136:             import pyautogui
137:             pyautogui.FAILSAFE = True
138:             pyautogui.PAUSE = 0.1
139:             logger.info(f"PyAutoGUI initialized. Screen size: {pyautogui.size()}")
140:         except Exception as e:
141:             logger.error(f"Failed to initialize PyAutoGUI: {e}")
142:             self.text_box.value += f"⚠️ Warning: Failed to initialize PyAutoGUI: {e}\n"
143: 
144: 
145: 
146:     def get_next_code_file(self) -> Optional[str]:
147: 
148:         if self.code_files:
149:             file_path = self.code_files[self.current_code_index]
150:             self.current_code_index = (self.current_code_index + 1) % len(self.code_files)
151:             return file_path
152:         return None
153: 
154:     def _split_file_into_chunks(self, file_path: str, chunk_size: int = 50) -> list:
155: 
156:         with open(file_path, "r") as f:
157:             lines = f.readlines()
158:         if len(lines) <= chunk_size:
159:             return [lines]
160:         chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
161:         logger.info(f"Split file {file_path} into {len(chunks)} chunks")
162:         return chunks
163: 
164:     async def calculate_typing_time(self, file_path: str) -> dict:
165:         try:
166:             with open(file_path, "r") as file:
167:                 lines = file.readlines()
168:             total_chars = sum(len(line.rstrip()) for line in lines)
169:             total_lines = len(lines)
170:             empty_lines = sum(1 for line in lines if not line.strip())
171:             non_empty_lines = total_lines - empty_lines
172: 
173:             avg_char_time = (self.typing_speed["min"] + self.typing_speed["max"]) / 2
174:             char_typing_time = total_chars * avg_char_time
175: 
176:             expected_mistakes = int(total_chars * self.typing_speed["mistake_rate"])
177:             mistake_time = expected_mistakes * (0.2 + 0.1)
178: 
179:             avg_line_break = sum(self.typing_speed["line_break"]) / 2
180:             line_break_time = non_empty_lines * avg_line_break
181:             empty_line_time = empty_lines * (avg_line_break * 0.5)
182: 
183:             total_time = char_typing_time + mistake_time + line_break_time + empty_line_time
184: 
185:             timing_details = {
186:                 "total_time_seconds": round(total_time, 2),
187:                 "total_time_formatted": self._format_time(total_time),
188:                 "breakdown": {
189:                     "characters": {"count": total_chars, "time_seconds": round(char_typing_time, 2)},
190:                     "lines": {"total": total_lines, "empty": empty_lines, "non_empty": non_empty_lines,
191:                               "time_seconds": round(line_break_time + empty_line_time, 2)},
192:                     "expected_mistakes": {"count": expected_mistakes, "time_seconds": round(mistake_time, 2)},
193:                     "typing_speed": {"chars_per_second": round(1 / avg_char_time, 2),
194:                                      "avg_pause_between_lines": round(avg_line_break, 2)},
195:                 },
196:             }
197:             logger.info(f"Estimated typing time: {timing_details['total_time_formatted']}")
198:             self.text_box.value += (
199:                 f"Estimated typing time: {timing_details['total_time_formatted']}\n"
200:                 f"Total characters: {total_chars}\n"
201:                 f"Total lines: {total_lines}\n"
202:                 f"Expected mistakes: {expected_mistakes}\n"
203:             )
204:             return timing_details
205: 
206:         except FileNotFoundError:
207:             logger.error(f"File not found: {file_path}")
208:             self.text_box.value += f"Error: File not found: {file_path}\n"
209:             return None
210:         except Exception as e:
211:             logger.error(f"Error calculating typing time: {e}")
212:             self.text_box.value += f"Error calculating typing time: {e}\n"
213:             return None
214: 
215:     def _format_time(self, seconds: float) -> str:
216:         hours = int(seconds // 3600)
217:         minutes = int((seconds % 3600) // 60)
218:         remaining_seconds = int(seconds % 60)
219:         if hours > 0:
220:             return f"{hours}h {minutes}m {remaining_seconds}s"
221:         elif minutes > 0:
222:             return f"{minutes}m {remaining_seconds}s"
223:         else:
224:             return f"{remaining_seconds}s"
225: 
226: 
227: 
228:     async def simulate_typing(self, file_path: Optional[str] = None):
229: 
230:         logger.debug(f"simulate_typing called with file_path: {file_path}")
231: 
232:         if self.simulation_mode == "Tab Switching Only":
233:             self.text_box.value += "Tab switching only mode selected. Skipping typing simulation...\n"
234:             return
235:         elif self.simulation_mode in ["Typing Only", "Hybrid"]:
236: 
237:             if not file_path:
238:                 logger.error("No file path provided for typing simulation")
239:                 self.text_box.value += "❌ Error: No file path provided for typing simulation.\n"
240:                 return
241: 
242:             if not os.path.exists(file_path):
243:                 logger.error(f"File not found: {file_path}")
244:                 self.text_box.value += f"❌ Error: File not found: {file_path}\n"
245:                 return
246: 
247:             logger.info(f"Simulating typing with file: {file_path}")
248:             self.text_box.value += f"Typing from file: {os.path.basename(file_path)}\n"
249: 
250: 
251:             chunks = self._split_file_into_chunks(file_path, chunk_size=50)
252:             for i, chunk in enumerate(chunks):
253:                 if not self.loop_flag:
254:                     break
255:                 chunk_text = "".join(chunk)
256:                 await self._simulate_code_typing_from_lines(chunk_text, i)
257:                 await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
258:         else:
259:             self.text_box.value += "Unknown simulation mode selected.\n"
260: 
261:     async def _simulate_code_typing_from_lines(self, text: str, chunk_index: int):
262:         lines = text.splitlines(keepends=True)
263:         original_indents = {i: len(line) - len(line.lstrip()) for i, line in enumerate(lines)}
264:         self.text_box.value += f"Typing chunk {chunk_index + 1}...\n"
265:         for i, line in enumerate(lines):
266:             if not self.loop_flag:
267:                 break
268:             line = " " * original_indents.get(i, 0) + line.strip()
269:             if not line:
270:                 pyautogui.press("enter")
271:                 await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
272:                 continue
273:             await self._type_line_with_simulation(line, i)
274:             await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
275: 
276:     async def _type_line_with_simulation(self, line: str, line_num: int):
277:         if self.formatter:
278:             line = self.formatter.format_line(line)
279:         for char in line:
280:             if not self.loop_flag:
281:                 break
282:             if random.random() < self.typing_speed["mistake_rate"]:
283:                 await self._simulate_typing_mistake(char)
284:             self._type_character(char)
285:             await asyncio.sleep(random.uniform(self.typing_speed["min"], self.typing_speed["max"]))
286:         pyautogui.press("enter")
287:         logger.info(f"Typed line: {line}")
288: 
289:     async def _simulate_typing_mistake(self, correct_char: str):
290:         wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
291:         pyautogui.write(wrong_char)
292:         await asyncio.sleep(0.2)
293:         pyautogui.press("backspace")
294:         await asyncio.sleep(0.1)
295: 
296:     def _type_character(self, char: str):
297:         if char == "\t":
298:             pyautogui.press("tab")
299:         elif char == "\n":
300:             pyautogui.press("enter")
301:         else:
302:             pyautogui.write(char)
303: 
304:     def switch_window(self):
305:         app = self.app_switcher.get_random_running_app()
306:         if app:
307:             if self.app_switcher.focus_application(app):
308:                 self.text_box.value += f"Switched to {app['name']}\n"
309:                 logger.info(f"Switched to {app['name']}")
310:             else:
311:                 self.text_box.value += f"Failed to switch to {app['name']}\n"
312:                 logger.error(f"Failed to switch to {app['name']}")
313:         else:
314:             self.text_box.value += "No configured applications running\n"
315:             logger.warning("No configured applications running")
316: 
317:     async def _simulate_random_actions(self):
318:         while self.loop_flag:
319:             actions = [
320:                 self._random_cursor_move,
321:                 self._random_scroll,
322:                 self._middle_click,
323:                 self._window_switch_action,
324:             ]
325:             for action in actions:
326:                 if not self.loop_flag:
327:                     break
328:                 await action()
329:             await asyncio.sleep(random.uniform(0.3, 0.7))
330: 
331:     async def _random_cursor_move(self):
332:         x = random.randint(100, 1000)
333:         y = random.randint(100, 1000)
334:         pyautogui.moveTo(x, y, duration=0.5)
335:         logger.info(f"Moved cursor to ({x}, {y})")
336: 
337:     async def _random_scroll(self):
338:         scroll_amount = random.randint(-100, 100)
339:         pyautogui.scroll(scroll_amount)
340:         logger.info(f"Scrolled {scroll_amount}")
341:         await asyncio.sleep(0.5)
342:         pyautogui.move(100, 50, duration=0.5)
343:         logger.info("Moved mouse relatively by (100, 50).")
344:         await asyncio.sleep(0.5)
345:         pyautogui.move(-50, -25, duration=0.5)
346:         logger.info("Moved mouse relatively by (-50, -25).")
347:         await asyncio.sleep(0.5)
348: 
349:     async def _middle_click(self):
350:         if random.random() < 0.3:
351:             pyautogui.click(button="middle")
352:             logger.info("Middle clicked")
353: 
354:     async def _window_switch_action(self):
355:         if random.random() < 0.2:
356:             self.switch_window()
357:             await asyncio.sleep(0.5)
358: 
359:     async def _cleanup_simulation(self):
360:         await asyncio.sleep(0.5)
361: 
362:     def _handle_simulation_end(self):
363:         self.loop_flag = False
364:         self.mouse_controller.stop()
365:         self.text_box.value += "Simulation ended\n"
366:         logger.info("Simulation ended")
367: 
368:     async def simulate_mouse_and_command_tab(self, duration=10):
369: 
370:         if not self.loop_flag:
371:             return
372: 
373:         self.text_box.value += "🖱️ Simulating mouse movements and Command+Tab...\n"
374:         logger.info("Starting mouse and Command+Tab simulation")
375: 
376:         start_time = time.time()
377: 
378:         try:
379: 
380:             self.mouse_controller.start(min_interval=1.0, max_interval=3.0)
381: 
382: 
383:             while self.loop_flag and (time.time() - start_time < duration):
384: 
385:                 for _ in range(random.randint(1, 3)):
386:                     if not self.loop_flag:
387:                         break
388:                     await self._random_cursor_move()
389:                     await asyncio.sleep(random.uniform(0.5, 1.5))
390: 
391: 
392:                 if random.random() < 0.7:
393:                     await self.simulate_command_tab()
394: 
395: 
396:                 await asyncio.sleep(random.uniform(1.0, 2.0))
397: 
398:         finally:
399: 
400:             self.mouse_controller.stop()
401:             logger.info("Mouse and Command+Tab simulation completed")
```

## File: src/codesimulator/app_switcher.py
```python
  1: import sys
  2: import subprocess
  3: from typing import Optional, List, Dict
  4: import random
  5: from .logging_config import logger
  6: 
  7: 
  8: class AppSwitcher:
  9: 
 10: 
 11:     def __init__(self, config):
 12: 
 13:         self.config = config
 14:         self.platform = sys.platform
 15:         self._quartz = None
 16:         self._win32gui = None
 17:         self._win32process = None
 18:         self._display = None
 19:         self._setup_platform_handler()
 20: 
 21:     def _setup_platform_handler(self):
 22: 
 23:         try:
 24:             if self.platform == 'darwin':
 25:                 self._setup_macos_handler()
 26:             elif self.platform == 'win32':
 27:                 self._setup_windows_handler()
 28:             else:
 29:                 self._setup_linux_handler()
 30:         except Exception as e:
 31:             logger.error(f"Failed to setup platform handler: {e}")
 32:             raise RuntimeError(f"Platform setup failed: {e}")
 33: 
 34:     def _setup_macos_handler(self):
 35: 
 36:         try:
 37:             import Quartz
 38:             self._quartz = Quartz
 39:         except ImportError as e:
 40:             logger.error(f"Failed to import Quartz module for macOS: {e}")
 41:             raise ImportError("Quartz module is required for macOS support")
 42: 
 43:     def _setup_windows_handler(self):
 44: 
 45:         try:
 46:             import win32gui
 47:             import win32process
 48:             self._win32gui = win32gui
 49:             self._win32process = win32process
 50:         except ImportError as e:
 51:             logger.error(f"Failed to import win32gui/win32process modules: {e}")
 52:             raise ImportError("win32gui and win32process modules are required for Windows support")
 53: 
 54:     def _setup_linux_handler(self):
 55: 
 56:         try:
 57:             import Xlib.display
 58:             self._display = Xlib.display.Display()
 59:         except ImportError as e:
 60:             logger.error(f"Failed to import Xlib module: {e}")
 61:             raise ImportError("Xlib module is required for Linux support")
 62: 
 63:     def _remove_duplicates(self, apps: List[Dict]) -> List[Dict]:
 64: 
 65:         seen = set()
 66:         unique_apps = []
 67:         for app in apps:
 68: 
 69:             identifier = tuple(sorted((k, str(v)) for k, v in app.items()))
 70:             if identifier not in seen:
 71:                 seen.add(identifier)
 72:                 unique_apps.append(app)
 73:         return unique_apps
 74: 
 75:     def get_running_applications(self) -> List[Dict]:
 76: 
 77:         if self.platform == 'darwin':
 78:             return self._get_running_applications_macos()
 79:         elif self.platform == 'win32':
 80:             return self._get_running_applications_windows()
 81:         else:
 82:             return self._get_running_applications_linux()
 83: 
 84:     def _get_running_applications_macos(self) -> List[Dict]:
 85: 
 86:         running_apps = []
 87:         try:
 88:             window_list = self._quartz.CGWindowListCopyWindowInfo(
 89:                 self._quartz.kCGWindowListOptionOnScreenOnly |
 90:                 self._quartz.kCGWindowListExcludeDesktopElements,
 91:                 self._quartz.kCGNullWindowID
 92:             )
 93: 
 94:             if window_list:
 95:                 window_list = list(window_list)
 96: 
 97:             for app in self.config.get_applications():
 98:                 app_name = app.get('process_name', '')
 99:                 bundle_id = app.get('bundle_id', '')
100: 
101:                 for window in window_list:
102:                     owner = window.get(self._quartz.kCGWindowOwnerName, '')
103:                     owner_bundle = window.get('kCGWindowOwnerBundleID', '')
104: 
105:                     if (owner and owner == app_name) or \
106:                             (bundle_id and owner_bundle == bundle_id):
107:                         running_apps.append(app.copy())
108:                         break
109: 
110:         except Exception as e:
111:             logger.error(f"Error getting macOS running applications: {e}")
112:             return []
113: 
114:         return self._remove_duplicates(running_apps)
115: 
116:     def _get_running_applications_windows(self) -> List[Dict]:
117: 
118:         running_apps = []
119:         try:
120:             def callback(hwnd, apps):
121:                 if not self._win32gui.IsWindowVisible(hwnd):
122:                     return True
123: 
124:                 try:
125:                     _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
126:                     class_name = self._win32gui.GetClassName(hwnd)
127: 
128:                     for app in self.config.get_applications():
129:                         if class_name == app.get('window_class'):
130:                             apps.append(app.copy())
131:                 except Exception as e:
132:                     logger.debug(f"Error processing window {hwnd}: {e}")
133:                 return True
134: 
135:             self._win32gui.EnumWindows(callback, running_apps)
136:         except Exception as e:
137:             logger.error(f"Error getting Windows running applications: {e}")
138:             return []
139: 
140:         return self._remove_duplicates(running_apps)
141: 
142:     def _get_running_applications_linux(self) -> List[Dict]:
143: 
144:         running_apps = []
145:         try:
146:             root = self._display.screen().root
147:             window_ids = root.get_full_property(
148:                 self._display.intern_atom('_NET_CLIENT_LIST'),
149:                 self._display.intern_atom('WINDOW')
150:             ).value
151: 
152:             for window_id in window_ids:
153:                 window = self._display.create_resource_object('window', window_id)
154:                 try:
155:                     window_class = window.get_wm_class()
156:                     if window_class:
157:                         for app in self.config.get_applications():
158:                             if app.get('window_class') in window_class:
159:                                 running_apps.append(app.copy())
160:                 except Exception as e:
161:                     logger.debug(f"Error processing window {window_id}: {e}")
162:                     continue
163: 
164:         except Exception as e:
165:             logger.error(f"Error getting Linux running applications: {e}")
166:             return []
167: 
168:         return self._remove_duplicates(running_apps)
169: 
170:     def get_random_running_app(self) -> Optional[Dict]:
171: 
172:         running_apps = self.get_running_applications()
173:         return random.choice(running_apps) if running_apps else None
174: 
175:     def focus_application(self, app_info: Dict) -> bool:
176: 
177:         if not app_info:
178:             logger.error("Cannot focus: app_info is None or empty")
179:             return False
180: 
181:         try:
182:             if self.platform == 'darwin':
183:                 app_name = app_info.get("name")
184:                 if not app_name:
185:                     raise ValueError("No application name provided")
186:                 subprocess.run(
187:                     ['osascript', '-e', f'tell application "{app_name}" to activate'],
188:                     check=True,
189:                     capture_output=True,
190:                     text=True
191:                 )
192: 
193:             elif self.platform == 'win32':
194:                 window_class = app_info.get('window_class')
195:                 if not window_class:
196:                     raise ValueError("No window class provided")
197: 
198:                 def callback(hwnd, class_name):
199:                     try:
200:                         if (self._win32gui.IsWindowVisible(hwnd) and
201:                                 self._win32gui.GetClassName(hwnd) == class_name):
202:                             self._win32gui.SetForegroundWindow(hwnd)
203:                             return False
204:                     except Exception as e:
205:                         logger.error(f"Error setting foreground window: {e}")
206:                     return True
207: 
208:                 self._win32gui.EnumWindows(callback, window_class)
209: 
210:             else:
211:                 app_name = app_info.get("name")
212:                 if not app_name:
213:                     raise ValueError("No application name provided")
214:                 subprocess.run(
215:                     ['wmctrl', '-a', app_name],
216:                     check=True,
217:                     capture_output=True,
218:                     text=True
219:                 )
220: 
221:             return True
222: 
223:         except subprocess.CalledProcessError as e:
224:             logger.error(f"Command failed with return code {e.returncode}: {e.output}")
225:             return False
226:         except Exception as e:
227:             logger.error(f"Error focusing application {app_info.get('name', 'unknown')}: {e}")
228:             return False
```

## File: src/codesimulator/app.py
```python
   1: import asyncio
   2: import os
   3: import json
   4: import tempfile
   5: import platform
   6: import random
   7: import subprocess
   8: import sys
   9: from typing import Optional
  10: import toga
  11: from toga.style import Pack
  12: from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT
  13: from toga.colors import rgb, rgba
  14: from .actions import ActionSimulator
  15: from .key_handler import GlobalKeyHandler
  16: from .logging_config import get_log_path, setup_file_logging, logger
  17: from .path_utils import log_environment_info, get_log_path
  18: 
  19: log_environment_info()
  20: 
  21: 
  22: class CodeSimulator(toga.App):
  23:     def __init__(self):
  24:         super().__init__(
  25:             formal_name="Code Simulator",
  26:             app_id="com.example.codesimulator"
  27:         )
  28: 
  29:         self.selected_file = None
  30:         self.current_view = "simulation"
  31: 
  32:     async def show_debug_info(self, widget):
  33:         info = {
  34:             "OS": platform.system(),
  35:             "OS Version": platform.version(),
  36:             "Python Version": platform.python_version(),
  37:             "App Directory": os.path.dirname(os.path.abspath(__file__)),
  38:             "Current Directory": os.getcwd(),
  39:             "Log File": get_log_path(),
  40:             "Is Packaged": getattr(sys, 'frozen', False),
  41:             "Executable": sys.executable
  42:         }
  43: 
  44:         self.console.value = "--- Debug Information ---\n\n"
  45:         for key, value in info.items():
  46:             self.console.value += f"{key}: {value}\n"
  47: 
  48:         log_environment_info()
  49:         self.console.value += "\nDetailed debug information has been logged to the log file.\n"
  50: 
  51:     async def view_console_logs(self, widget):
  52:         try:
  53:             if platform.system() == "Darwin":
  54:                 process = subprocess.Popen(
  55:                     ["log", "show", "--predicate", "process == 'Code Simulator'", "--last", "1h"],
  56:                     stdout=subprocess.PIPE,
  57:                     stderr=subprocess.PIPE,
  58:                     text=True
  59:                 )
  60:                 stdout, stderr = process.communicate(timeout=5)
  61: 
  62:                 if stdout:
  63:                     self.console.value = "Recent Console Logs:\n\n" + stdout
  64:                 else:
  65:                     self.console.value = "No recent console logs found.\n"
  66:                     if stderr:
  67:                         self.console.value += f"Error: {stderr}\n"
  68:             else:
  69:                 self.console.value = "Console log viewing only supported on macOS."
  70:         except Exception as e:
  71:             self.console.value = f"Error viewing console logs: {e}"
  72: 
  73:     async def view_logs(self, widget):
  74:         setup_file_logging()
  75:         log_path = get_log_path()
  76: 
  77:         self.console.value = "Log Information\n"
  78:         self.console.value += "=============\n\n"
  79:         self.console.value += f"Log file location: {log_path}\n\n"
  80: 
  81:         logger.info("Test log message from View Logs button")
  82: 
  83:         if not os.path.exists(log_path):
  84:             self.console.value += f"❌ Log file still not found after write attempt!\n\n"
  85: 
  86:             try:
  87:                 log_dir = os.path.dirname(log_path)
  88:                 test_file_path = os.path.join(log_dir, "test_write.txt")
  89:                 with open(test_file_path, 'w') as f:
  90:                     f.write("Test write")
  91:                 self.console.value += f"✓ Successfully created test file at: {test_file_path}\n"
  92:                 os.remove(test_file_path)
  93:             except Exception as e:
  94:                 self.console.value += f"❌ Could not write test file: {e}\n"
  95:                 self.console.value += "This suggests a permissions issue or the directory doesn't exist\n"
  96: 
  97:             self.console.value += "\nEnvironment Information:\n"
  98:             self.console.value += f"Working directory: {os.getcwd()}\n"
  99:             self.console.value += f"Home directory: {os.path.expanduser('~')}\n"
 100:             self.console.value += f"App directory: {os.path.dirname(__file__)}\n"
 101:             self.console.value += f"Python executable: {sys.executable}\n"
 102:             self.console.value += f"Is packaged: {getattr(sys, 'frozen', False)}\n"
 103: 
 104:             self.console.value += "\nTry looking for logs in these locations:\n"
 105:             self.console.value += f"1. {os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')}\n"
 106:             self.console.value += f"2. {tempfile.gettempdir()}\n"
 107: 
 108:             return
 109: 
 110:         file_size = os.path.getsize(log_path)
 111:         last_modified = os.path.getmtime(log_path)
 112:         import datetime
 113:         mod_time = datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
 114: 
 115:         self.console.value += f"Log file size: {file_size} bytes\n"
 116:         self.console.value += f"Last modified: {mod_time}\n\n"
 117: 
 118:         try:
 119:             with open(log_path, 'r') as f:
 120:                 if file_size > 10000:
 121:                     self.console.value += f"Log file is large. Showing last portion...\n\n"
 122:                     f.seek(max(0, file_size - 10000))
 123:                     f.readline()
 124:                     content = f.read()
 125:                 else:
 126:                     content = f.read()
 127: 
 128:             self.console.value += "Log Content:\n"
 129:             self.console.value += "===========\n\n"
 130:             self.console.value += content
 131: 
 132:         except Exception as e:
 133:             self.console.value += f"❌ Error reading log file: {e}\n"
 134: 
 135:     def startup(self):
 136:         from .logging_config import setup_file_logging
 137:         setup_file_logging()
 138: 
 139:         self.setup_ui()
 140:         self.setup_components()
 141:         logger.info("Application started successfully.")
 142: 
 143:     def setup_colors(self):
 144: 
 145:         self.colors = {
 146:             'primary': rgb(41, 98, 255),
 147:             'secondary': rgb(0, 163, 92),
 148:             'accent': rgb(83, 186, 122),
 149:             'danger': rgb(235, 64, 52),
 150:             'background': rgb(245, 247, 250),
 151:             'card': rgb(255, 255, 255),
 152:             'text': rgb(33, 33, 33),
 153:             'text_light': rgb(108, 117, 125),
 154:             'border': rgb(222, 226, 230),
 155:             'menu_bg': rgb(32, 41, 64),
 156:             'menu_text': rgb(255, 255, 255),
 157:             'menu_selected': rgb(53, 63, 88),
 158:             'menu_hover': rgb(47, 56, 80),
 159:             'status_success': rgb(25, 135, 84),
 160:             'status_warning': rgb(255, 193, 7),
 161:             'status_error': rgb(220, 53, 69),
 162:             'toolbar': rgb(52, 58, 64),
 163:             'toolbar_text': rgb(255, 255, 255),
 164:         }
 165: 
 166:     def setup_ui(self):
 167: 
 168:         self.setup_colors()
 169: 
 170: 
 171:         main_box = toga.Box(style=Pack(direction=ROW, flex=1))
 172: 
 173: 
 174:         self.side_menu = self.create_side_menu()
 175: 
 176:         self.side_menu.style.width = 220
 177:         main_box.add(self.side_menu)
 178: 
 179: 
 180:         self.content_container = toga.Box(style=Pack(
 181:             direction=COLUMN,
 182:             flex=1,
 183:             background_color=self.colors['background']
 184:         ))
 185:         main_box.add(self.content_container)
 186: 
 187: 
 188:         self.simulation_view = self.create_simulation_view()
 189:         self.configuration_view = self.create_configuration_view()
 190:         self.logs_view = self.create_logs_view()
 191:         self.about_view = self.create_about_view()
 192: 
 193: 
 194:         self.show_view("simulation")
 195: 
 196: 
 197:         self.main_window = toga.MainWindow(title=self.formal_name)
 198:         self.main_window.content = main_box
 199: 
 200: 
 201:         cmd_s = toga.Command(
 202:             self.start_simulation,
 203:             "Start Simulation",
 204:             shortcut=toga.Key.MOD_1 + "s"
 205:         )
 206:         cmd_x = toga.Command(
 207:             self.stop_simulation,
 208:             "Stop Simulation",
 209:             shortcut=toga.Key.MOD_1 + "x"
 210:         )
 211:         self.commands.add(cmd_s, cmd_x)
 212: 
 213: 
 214:         self.main_window.show()
 215: 
 216:     def create_side_menu(self):
 217: 
 218:         side_menu = toga.Box(style=Pack(
 219:             direction=COLUMN,
 220:             background_color=self.colors['menu_bg'],
 221:             padding=(0, 0),
 222:             flex=1
 223:         ))
 224: 
 225: 
 226:         logo_box = toga.Box(style=Pack(
 227:             direction=COLUMN,
 228:             padding=(20, 15),
 229:             alignment=CENTER
 230:         ))
 231: 
 232:         title = toga.Label(
 233:             "Code Simulator",
 234:             style=Pack(
 235:                 font_size=18,
 236:                 font_weight="bold",
 237:                 color=self.colors['menu_text'],
 238:                 text_align=CENTER
 239:             )
 240:         )
 241: 
 242:         subtitle = toga.Label(
 243:             "v0.0.1",
 244:             style=Pack(
 245:                 font_size=12,
 246:                 color=rgba(255, 255, 255, 0.7),
 247:                 text_align=CENTER,
 248:                 padding_top=5
 249:             )
 250:         )
 251: 
 252:         logo_box.add(title)
 253:         logo_box.add(subtitle)
 254:         side_menu.add(logo_box)
 255: 
 256: 
 257:         divider = toga.Divider(style=Pack(
 258:             padding=(0, 15),
 259:         ))
 260:         divider.style.color = rgba(255, 255, 255, 0.2)
 261:         side_menu.add(divider)
 262: 
 263: 
 264:         self.menu_items = {}
 265:         menu_options = [
 266:             ("simulation", "Simulation", "⌨️"),
 267:             ("configuration", "Configuration", "⚙️"),
 268:             ("logs", "Logs & Debug", "📊"),
 269:             ("about", "About & Help", "ℹ️")
 270:         ]
 271: 
 272: 
 273:         for item_id, label, icon in menu_options:
 274:             menu_item = self.create_menu_item(item_id, label, icon)
 275:             side_menu.add(menu_item)
 276:             self.menu_items[item_id] = menu_item
 277: 
 278: 
 279:         side_menu.add(toga.Box(style=Pack(flex=1)))
 280: 
 281: 
 282:         status_box = toga.Box(style=Pack(
 283:             direction=COLUMN,
 284:             padding=(15, 15),
 285:         ))
 286: 
 287:         status_box.style.background_color = rgba(0, 0, 0, 0.2)
 288: 
 289:         status_label = toga.Label(
 290:             "Ready",
 291:             style=Pack(
 292:                 font_size=12,
 293:                 color=self.colors['menu_text'],
 294:                 padding=(5, 5)
 295:             )
 296:         )
 297:         self.status_label = status_label
 298:         status_box.add(status_label)
 299: 
 300:         side_menu.add(status_box)
 301: 
 302:         return side_menu
 303: 
 304:     def create_menu_item(self, item_id, label, icon):
 305: 
 306: 
 307:         menu_item = toga.Box(style=Pack(
 308:             direction=ROW,
 309:             padding=(12, 15),
 310:             alignment=CENTER,
 311:         ))
 312: 
 313: 
 314:         icon_label = toga.Label(
 315:             icon,
 316:             style=Pack(
 317:                 font_size=16,
 318:                 color=self.colors['menu_text'],
 319:                 width=25,
 320:                 text_align=CENTER
 321:             )
 322:         )
 323: 
 324: 
 325:         text_label = toga.Label(
 326:             label,
 327:             style=Pack(
 328:                 font_size=14,
 329:                 color=self.colors['menu_text'],
 330:                 padding_left=10,
 331:                 text_align=LEFT,
 332:                 flex=1
 333:             )
 334:         )
 335: 
 336:         menu_item.add(icon_label)
 337:         menu_item.add(text_label)
 338: 
 339: 
 340:         button = toga.Button(
 341:             "",
 342:             on_press=lambda widget: self.show_view(item_id),
 343:             style=Pack(
 344:                 padding=0,
 345:                 flex=1
 346:             )
 347:         )
 348: 
 349:         button.style.background_color = rgba(0, 0, 0, 0)
 350: 
 351:         menu_item.add(button)
 352: 
 353: 
 354:         if item_id == self.current_view:
 355:             menu_item.style.background_color = self.colors['menu_selected']
 356: 
 357:         return menu_item
 358: 
 359:     def show_view(self, view_name):
 360: 
 361:         # First, clear the content container
 362:         for child in self.content_container.children:
 363:             self.content_container.remove(child)
 364: 
 365:         # Update menu selection styling
 366:         for item_id, menu_item in self.menu_items.items():
 367:             if item_id == view_name:
 368:                 # Set the background color for the selected item
 369:                 menu_item.style.background_color = self.colors['menu_selected']
 370:             else:
 371:                 # For non-selected items, reset to menu background color
 372:                 menu_item.style.background_color = self.colors['menu_bg']
 373: 
 374:         # Set the current view and add the appropriate content
 375:         self.current_view = view_name
 376: 
 377:         if view_name == "simulation":
 378:             self.content_container.add(self.simulation_view)
 379:         elif view_name == "configuration":
 380:             self.content_container.add(self.configuration_view)
 381:         elif view_name == "logs":
 382:             self.content_container.add(self.logs_view)
 383:         elif view_name == "about":
 384:             self.content_container.add(self.about_view)
 385: 
 386:     def create_simulation_view(self):
 387: 
 388:         simulation_view = toga.Box(style=Pack(
 389:             direction=COLUMN,
 390:             background_color=self.colors['background'],
 391:             padding=(20, 20),
 392:             flex=1
 393:         ))
 394: 
 395:         # Top toolbar section
 396:         toolbar = toga.Box(style=Pack(
 397:             direction=ROW,
 398:             padding=(15, 10),
 399:             background_color=self.colors['primary'],
 400:             alignment=CENTER
 401:         ))
 402: 
 403:         # Toolbar title
 404:         toolbar_title = toga.Label(
 405:             "Simulation Control",
 406:             style=Pack(
 407:                 font_size=16,
 408:                 font_weight="bold",
 409:                 color=self.colors['toolbar_text'],
 410:                 flex=1
 411:             )
 412:         )
 413:         toolbar.add(toolbar_title)
 414: 
 415:         # Toolbar buttons
 416:         self.start_button = toga.Button(
 417:             "Start Simulation",
 418:             on_press=self.start_simulation,
 419:             style=Pack(
 420:                 padding=(10, 15),
 421:                 background_color=self.colors['secondary'],
 422:                 color=self.colors['toolbar_text'],
 423:                 font_weight="bold"
 424:             )
 425:         )
 426: 
 427:         self.stop_button = toga.Button(
 428:             "Stop",
 429:             on_press=self.stop_simulation,
 430:             style=Pack(
 431:                 padding=(10, 15),
 432:                 background_color=self.colors['danger'],
 433:                 color=self.colors['toolbar_text'],
 434:                 font_weight="bold"
 435:             ),
 436:             enabled=False
 437:         )
 438: 
 439:         toolbar.add(self.start_button)
 440:         toolbar.add(toga.Box(style=Pack(width=10)))  # Spacer
 441:         toolbar.add(self.stop_button)
 442: 
 443:         simulation_view.add(toolbar)
 444: 
 445:         # Main content with card design
 446:         content_card = toga.Box(style=Pack(
 447:             direction=COLUMN,
 448:             background_color=self.colors['card'],
 449:             padding=(20, 20),
 450:             flex=1,
 451: 
 452: 
 453:         ))
 454: 
 455:         # Simulation settings section
 456:         settings_box = toga.Box(style=Pack(
 457:             direction=COLUMN,
 458:             padding=(0, 0, 10, 0)
 459:         ))
 460: 
 461:         settings_title = toga.Label(
 462:             "Simulation Settings",
 463:             style=Pack(
 464:                 font_size=16,
 465:                 font_weight="bold",
 466:                 color=self.colors['text'],
 467:                 padding_bottom=10
 468:             )
 469:         )
 470:         settings_box.add(settings_title)
 471: 
 472:         # Mode selection
 473:         mode_box = toga.Box(style=Pack(
 474:             direction=ROW,
 475:             padding=(0, 0, 15, 0),
 476:             alignment=CENTER
 477:         ))
 478: 
 479:         mode_label = toga.Label(
 480:             "Mode:",
 481:             style=Pack(
 482:                 width=100,
 483:                 color=self.colors['text']
 484:             )
 485:         )
 486: 
 487:         self.simulation_modes = [
 488:             "Typing Only",
 489:             "Tab Switching Only",
 490:             "Hybrid",
 491:             "Mouse and Command+Tab"
 492:         ]
 493: 
 494:         self.mode_selector = toga.Selection(
 495:             items=self.simulation_modes,
 496:             value=self.simulation_modes[2],
 497:             style=Pack(
 498:                 flex=1,
 499:                 padding=(5, 5)
 500:             )
 501:         )
 502: 
 503:         mode_box.add(mode_label)
 504:         mode_box.add(self.mode_selector)
 505:         settings_box.add(mode_box)
 506: 
 507:         # File selection
 508:         file_box = toga.Box(style=Pack(
 509:             direction=ROW,
 510:             padding=(0, 0, 15, 0),
 511:             alignment=CENTER
 512:         ))
 513: 
 514:         file_label = toga.Label(
 515:             "File:",
 516:             style=Pack(
 517:                 width=100,
 518:                 color=self.colors['text']
 519:             )
 520:         )
 521: 
 522:         self.file_display = toga.Label(
 523:             "Using default resources/code files",
 524:             style=Pack(
 525:                 flex=1,
 526:                 color=self.colors['text_light'],
 527:                 padding=(5, 5)
 528:             )
 529:         )
 530: 
 531:         choose_file_button = toga.Button(
 532:             "Choose File",
 533:             on_press=self.choose_file,
 534:             style=Pack(
 535:                 padding=(5, 10),
 536:                 background_color=self.colors['accent'],
 537:                 color=self.colors['toolbar_text']
 538:             )
 539:         )
 540: 
 541:         file_box.add(file_label)
 542:         file_box.add(self.file_display)
 543:         file_box.add(toga.Box(style=Pack(width=10)))  # Spacer
 544:         file_box.add(choose_file_button)
 545:         settings_box.add(file_box)
 546: 
 547:         content_card.add(settings_box)
 548: 
 549:         # Divider
 550:         content_card.add(toga.Divider(style=Pack(
 551:             padding=(10, 0)
 552:         )))
 553: 
 554:         # Console output section
 555:         console_box = toga.Box(style=Pack(
 556:             direction=COLUMN,
 557:             padding=(10, 0, 0, 0),
 558:             flex=1
 559:         ))
 560: 
 561:         console_title = toga.Label(
 562:             "Simulation Log",
 563:             style=Pack(
 564:                 font_size=16,
 565:                 font_weight="bold",
 566:                 color=self.colors['text'],
 567:                 padding_bottom=10
 568:             )
 569:         )
 570:         console_box.add(console_title)
 571: 
 572:         self.console = toga.MultilineTextInput(
 573:             readonly=True,
 574:             style=Pack(
 575:                 flex=1,
 576:                 background_color=rgb(250, 250, 250)
 577:             )
 578:         )
 579:         console_box.add(self.console)
 580: 
 581:         content_card.add(console_box)
 582:         simulation_view.add(content_card)
 583: 
 584:         # Status footer
 585:         status_bar = toga.Box(style=Pack(
 586:             direction=ROW,
 587:             padding=(10, 10),
 588:             background_color=self.colors['card'],
 589: 
 590: 
 591:         ))
 592: 
 593:         keyboard_shortcut_label = toga.Label(
 594:             "Keyboard Shortcuts: ⌘+S = Start Simulation | ⌘+X = Stop Simulation",
 595:             style=Pack(
 596:                 font_size=12,
 597:                 color=self.colors['text_light']
 598:             )
 599:         )
 600:         status_bar.add(keyboard_shortcut_label)
 601: 
 602:         simulation_view.add(status_bar)
 603: 
 604:         return simulation_view
 605: 
 606:     def create_configuration_view(self):
 607: 
 608:         configuration_view = toga.Box(style=Pack(
 609:             direction=COLUMN,
 610:             background_color=self.colors['background'],
 611:             padding=(20, 20),
 612:             flex=1
 613:         ))
 614: 
 615:         # Top toolbar
 616:         toolbar = toga.Box(style=Pack(
 617:             direction=ROW,
 618:             padding=(15, 10),
 619:             background_color=self.colors['primary'],
 620:             alignment=CENTER
 621:         ))
 622: 
 623:         toolbar_title = toga.Label(
 624:             "Configuration",
 625:             style=Pack(
 626:                 font_size=16,
 627:                 font_weight="bold",
 628:                 color=self.colors['toolbar_text'],
 629:                 flex=1
 630:             )
 631:         )
 632:         toolbar.add(toolbar_title)
 633: 
 634:         # Save configuration button
 635:         save_config_button = toga.Button(
 636:             "Save Settings",
 637:             on_press=self.save_configuration_direct,
 638:             style=Pack(
 639:                 padding=(10, 15),
 640:                 background_color=self.colors['secondary'],
 641:                 color=self.colors['toolbar_text'],
 642:                 font_weight="bold"
 643:             )
 644:         )
 645:         toolbar.add(save_config_button)
 646: 
 647:         configuration_view.add(toolbar)
 648: 
 649:         # Main content with card design
 650:         content_card = toga.Box(style=Pack(
 651:             direction=COLUMN,
 652:             background_color=self.colors['card'],
 653:             padding=(20, 20),
 654:             flex=1,
 655: 
 656: 
 657:         ))
 658: 
 659:         # Create a scroll container to hold all settings
 660:         scroll_container = toga.ScrollContainer(style=Pack(flex=1))
 661:         settings_box = toga.Box(style=Pack(direction=COLUMN, padding=(0, 10)))
 662: 
 663:         # Code Configuration Section
 664:         code_section = toga.Box(style=Pack(
 665:             direction=COLUMN,
 666:             padding=(0, 0, 20, 0)
 667:         ))
 668: 
 669:         code_title = toga.Label(
 670:             "Code Configuration",
 671:             style=Pack(
 672:                 font_size=16,
 673:                 font_weight="bold",
 674:                 color=self.colors['text'],
 675:                 padding_bottom=10
 676:             )
 677:         )
 678:         code_section.add(code_title)
 679: 
 680:         # Language selection
 681:         language_box = toga.Box(style=Pack(
 682:             direction=ROW,
 683:             padding=(0, 0, 10, 0),
 684:             alignment=CENTER
 685:         ))
 686: 
 687:         language_label = toga.Label(
 688:             "Language:",
 689:             style=Pack(
 690:                 width=150,
 691:                 color=self.colors['text']
 692:             )
 693:         )
 694: 
 695:         self.language_input = toga.Selection(
 696:             items=["python", "java", "php"],
 697:             value="python",
 698:             style=Pack(
 699:                 flex=1,
 700:                 padding=(5, 5)
 701:             )
 702:         )
 703: 
 704:         language_box.add(language_label)
 705:         language_box.add(self.language_input)
 706:         code_section.add(language_box)
 707: 
 708:         # Indent size
 709:         indent_box = toga.Box(style=Pack(
 710:             direction=ROW,
 711:             padding=(0, 0, 10, 0),
 712:             alignment=CENTER
 713:         ))
 714: 
 715:         indent_label = toga.Label(
 716:             "Indent Size:",
 717:             style=Pack(
 718:                 width=150,
 719:                 color=self.colors['text']
 720:             )
 721:         )
 722: 
 723:         self.indent_input = toga.NumberInput(
 724:             min_value=1,
 725:             max_value=8,
 726:             step=1,
 727:             value=4,
 728:             style=Pack(
 729:                 flex=1,
 730:                 padding=(5, 5)
 731:             )
 732:         )
 733: 
 734:         indent_box.add(indent_label)
 735:         indent_box.add(self.indent_input)
 736:         code_section.add(indent_box)
 737: 
 738:         # Max line length
 739:         max_line_box = toga.Box(style=Pack(
 740:             direction=ROW,
 741:             padding=(0, 0, 10, 0),
 742:             alignment=CENTER
 743:         ))
 744: 
 745:         max_line_label = toga.Label(
 746:             "Max Line Length:",
 747:             style=Pack(
 748:                 width=150,
 749:                 color=self.colors['text']
 750:             )
 751:         )
 752: 
 753:         self.max_line_input = toga.NumberInput(
 754:             min_value=40,
 755:             max_value=120,
 756:             step=1,
 757:             value=80,
 758:             style=Pack(
 759:                 flex=1,
 760:                 padding=(5, 5)
 761:             )
 762:         )
 763: 
 764:         max_line_box.add(max_line_label)
 765:         max_line_box.add(self.max_line_input)
 766:         code_section.add(max_line_box)
 767: 
 768:         settings_box.add(code_section)
 769: 
 770:         # Divider
 771:         settings_box.add(toga.Divider(style=Pack(
 772:             padding=(0, 10)
 773:         )))
 774: 
 775:         # Typing Speed Configuration Section
 776:         typing_section = toga.Box(style=Pack(
 777:             direction=COLUMN,
 778:             padding=(0, 0, 20, 0)
 779:         ))
 780: 
 781:         typing_title = toga.Label(
 782:             "Typing Speed Configuration",
 783:             style=Pack(
 784:                 font_size=16,
 785:                 font_weight="bold",
 786:                 color=self.colors['text'],
 787:                 padding_bottom=10
 788:             )
 789:         )
 790:         typing_section.add(typing_title)
 791: 
 792:         # Min typing speed
 793:         min_speed_box = toga.Box(style=Pack(
 794:             direction=ROW,
 795:             padding=(0, 0, 10, 0),
 796:             alignment=CENTER
 797:         ))
 798: 
 799:         min_speed_label = toga.Label(
 800:             "Min Speed (sec):",
 801:             style=Pack(
 802:                 width=150,
 803:                 color=self.colors['text']
 804:             )
 805:         )
 806: 
 807:         self.min_speed_input = toga.NumberInput(
 808:             min_value=0.01,
 809:             max_value=0.5,
 810:             step=0.01,
 811:             value=0.15,
 812:             style=Pack(
 813:                 flex=1,
 814:                 padding=(5, 5)
 815:             )
 816:         )
 817: 
 818:         min_speed_box.add(min_speed_label)
 819:         min_speed_box.add(self.min_speed_input)
 820:         typing_section.add(min_speed_box)
 821: 
 822:         # Max typing speed
 823:         max_speed_box = toga.Box(style=Pack(
 824:             direction=ROW,
 825:             padding=(0, 0, 10, 0),
 826:             alignment=CENTER
 827:         ))
 828: 
 829:         max_speed_label = toga.Label(
 830:             "Max Speed (sec):",
 831:             style=Pack(
 832:                 width=150,
 833:                 color=self.colors['text']
 834:             )
 835:         )
 836: 
 837:         self.max_speed_input = toga.NumberInput(
 838:             min_value=0.01,
 839:             max_value=0.5,
 840:             step=0.01,
 841:             value=0.25,
 842:             style=Pack(
 843:                 flex=1,
 844:                 padding=(5, 5)
 845:             )
 846:         )
 847: 
 848:         max_speed_box.add(max_speed_label)
 849:         max_speed_box.add(self.max_speed_input)
 850:         typing_section.add(max_speed_box)
 851: 
 852:         # Mistake rate
 853:         mistake_box = toga.Box(style=Pack(
 854:             direction=ROW,
 855:             padding=(0, 0, 10, 0),
 856:             alignment=CENTER
 857:         ))
 858: 
 859:         mistake_label = toga.Label(
 860:             "Mistake Rate:",
 861:             style=Pack(
 862:                 width=150,
 863:                 color=self.colors['text']
 864:             )
 865:         )
 866: 
 867:         self.mistake_input = toga.NumberInput(
 868:             min_value=0,
 869:             max_value=0.5,
 870:             step=0.01,
 871:             value=0.09,
 872:             style=Pack(
 873:                 flex=1,
 874:                 padding=(5, 5)
 875:             )
 876:         )
 877: 
 878:         mistake_box.add(mistake_label)
 879:         mistake_box.add(self.mistake_input)
 880:         typing_section.add(mistake_box)
 881: 
 882:         settings_box.add(typing_section)
 883: 
 884:         # Divider
 885:         settings_box.add(toga.Divider(style=Pack(
 886:             padding=(0, 10)
 887:         )))
 888: 
 889:         # Applications Configuration Section
 890:         apps_section = toga.Box(style=Pack(
 891:             direction=COLUMN,
 892:             padding=(0, 0, 20, 0)
 893:         ))
 894: 
 895:         apps_title = toga.Label(
 896:             "Applications Configuration",
 897:             style=Pack(
 898:                 font_size=16,
 899:                 font_weight="bold",
 900:                 color=self.colors['text'],
 901:                 padding_bottom=10
 902:             )
 903:         )
 904:         apps_section.add(apps_title)
 905: 
 906:         # Applications list (placeholder)
 907:         apps_info = toga.Label(
 908:             "Application settings are configured in applications.json.\nThe simulator will switch between these applications during simulation.",
 909:             style=Pack(
 910:                 color=self.colors['text'],
 911:                 padding_bottom=10
 912:             )
 913:         )
 914:         apps_section.add(apps_info)
 915: 
 916:         settings_box.add(apps_section)
 917: 
 918:         # Add the settings box to the scroll container
 919:         scroll_container.content = settings_box
 920:         content_card.add(scroll_container)
 921: 
 922:         # Add content card to the view
 923:         configuration_view.add(content_card)
 924: 
 925:         # Load the initial configuration values
 926:         # Note: We'll load values in setup_components after ActionSimulator is initialized
 927: 
 928:         return configuration_view
 929: 
 930:     def create_logs_view(self):
 931: 
 932:         logs_view = toga.Box(style=Pack(
 933:             direction=COLUMN,
 934:             background_color=self.colors['background'],
 935:             padding=(20, 20),
 936:             flex=1
 937:         ))
 938: 
 939: 
 940:         toolbar = toga.Box(style=Pack(
 941:             direction=ROW,
 942:             padding=(15, 10),
 943:             background_color=self.colors['primary'],
 944:             alignment=CENTER
 945:         ))
 946: 
 947:         toolbar_title = toga.Label(
 948:             "Logs & Debugging",
 949:             style=Pack(
 950:                 font_size=16,
 951:                 font_weight="bold",
 952:                 color=self.colors['toolbar_text'],
 953:                 flex=1
 954:             )
 955:         )
 956:         toolbar.add(toolbar_title)
 957: 
 958:         logs_view.add(toolbar)
 959: 
 960: 
 961:         content_card = toga.Box(style=Pack(
 962:             direction=COLUMN,
 963:             background_color=self.colors['card'],
 964:             padding=(20, 20),
 965:             flex=1,
 966: 
 967: 
 968:         ))
 969: 
 970: 
 971:         buttons_box = toga.Box(style=Pack(
 972:             direction=ROW,
 973:             padding=(0, 0, 15, 0)
 974:         ))
 975: 
 976:         view_logs_button = toga.Button(
 977:             "View Application Logs",
 978:             on_press=self.view_logs,
 979:             style=Pack(
 980:                 padding=(10, 15),
 981:                 background_color=self.colors['primary'],
 982:                 color=self.colors['toolbar_text'],
 983:             )
 984:         )
 985: 
 986:         debug_info_button = toga.Button(
 987:             "Show Debug Info",
 988:             on_press=self.show_debug_info,
 989:             style=Pack(
 990:                 padding=(10, 15),
 991:                 background_color=self.colors['primary'],
 992:                 color=self.colors['toolbar_text'],
 993:             )
 994:         )
 995: 
 996:         console_logs_button = toga.Button(
 997:             "View Console Logs",
 998:             on_press=self.view_console_logs,
 999:             style=Pack(
1000:                 padding=(10, 15),
1001:                 background_color=self.colors['primary'],
1002:                 color=self.colors['toolbar_text']
1003:             )
1004:         )
1005: 
1006:         buttons_box.add(view_logs_button)
1007:         buttons_box.add(debug_info_button)
1008:         buttons_box.add(console_logs_button)
1009:         content_card.add(buttons_box)
1010: 
1011: 
1012:         content_card.add(toga.Divider(style=Pack(
1013:             padding=(10, 0)
1014:         )))
1015: 
1016: 
1017:         log_box = toga.Box(style=Pack(
1018:             direction=COLUMN,
1019:             padding=(10, 0, 0, 0),
1020:             flex=1
1021:         ))
1022: 
1023:         log_title = toga.Label(
1024:             "Log Output",
1025:             style=Pack(
1026:                 font_size=16,
1027:                 font_weight="bold",
1028:                 color=self.colors['text'],
1029:                 padding_bottom=10
1030:             )
1031:         )
1032:         log_box.add(log_title)
1033: 
1034:         log_instructions = toga.Label(
1035:             "Click one of the buttons above to view logs or debug information.",
1036:             style=Pack(
1037:                 color=self.colors['text_light'],
1038:                 padding_bottom=10
1039:             )
1040:         )
1041:         log_box.add(log_instructions)
1042: 
1043: 
1044: 
1045:         log_console = toga.MultilineTextInput(
1046:             readonly=True,
1047:             style=Pack(
1048:                 flex=1,
1049:                 background_color=rgb(250, 250, 250)
1050:             )
1051:         )
1052:         # Share the console between views
1053:         self.console = log_console
1054:         log_box.add(log_console)
1055: 
1056:         content_card.add(log_box)
1057:         logs_view.add(content_card)
1058: 
1059:         return logs_view
1060: 
1061:     def create_about_view(self):
1062: 
1063:         about_view = toga.Box(style=Pack(
1064:             direction=COLUMN,
1065:             background_color=self.colors['background'],
1066:             padding=(20, 20),
1067:             flex=1
1068:         ))
1069: 
1070:         # Top toolbar
1071:         toolbar = toga.Box(style=Pack(
1072:             direction=ROW,
1073:             padding=(15, 10),
1074:             background_color=self.colors['primary'],
1075:             alignment=CENTER
1076:         ))
1077: 
1078:         toolbar_title = toga.Label(
1079:             "About & Help",
1080:             style=Pack(
1081:                 font_size=16,
1082:                 font_weight="bold",
1083:                 color=self.colors['toolbar_text'],
1084:                 flex=1
1085:             )
1086:         )
1087:         toolbar.add(toolbar_title)
1088: 
1089:         about_view.add(toolbar)
1090: 
1091:         # Main content with card design
1092:         content_card = toga.Box(style=Pack(
1093:             direction=COLUMN,
1094:             background_color=self.colors['card'],
1095:             padding=(20, 20),
1096:             flex=1,
1097: 
1098: 
1099:         ))
1100: 
1101:         # Create a scroll container for about content
1102:         scroll_container = toga.ScrollContainer(style=Pack(flex=1))
1103:         about_content = toga.Box(style=Pack(direction=COLUMN, padding=(0, 0)))
1104: 
1105:         # App information section
1106:         app_info_box = toga.Box(style=Pack(
1107:             direction=COLUMN,
1108:             padding=(0, 0, 20, 0)
1109:         ))
1110: 
1111:         app_name = toga.Label(
1112:             "Code Simulator",
1113:             style=Pack(
1114:                 font_size=24,
1115:                 font_weight="bold",
1116:                 color=self.colors['text'],
1117:                 padding_bottom=5
1118:             )
1119:         )
1120:         app_info_box.add(app_name)
1121: 
1122:         app_version = toga.Label(
1123:             "Version 0.0.1",
1124:             style=Pack(
1125:                 font_size=14,
1126:                 color=self.colors['text_light'],
1127:                 padding_bottom=10
1128:             )
1129:         )
1130:         app_info_box.add(app_version)
1131: 
1132:         app_description = toga.Label(
1133:             "Code Simulator is a tool for simulating coding activity including typing, window switching, and mouse movements. It's designed to create a realistic coding environment simulation.",
1134:             style=Pack(
1135:                 color=self.colors['text'],
1136:                 padding_bottom=10
1137:             )
1138:         )
1139:         app_info_box.add(app_description)
1140: 
1141:         copyright_label = toga.Label(
1142:             "© 2025 rylxes. All rights reserved.",
1143:             style=Pack(
1144:                 font_size=12,
1145:                 color=self.colors['text_light'],
1146:                 padding_bottom=20
1147:             )
1148:         )
1149:         app_info_box.add(copyright_label)
1150: 
1151:         about_content.add(app_info_box)
1152: 
1153:         # Divider
1154:         about_content.add(toga.Divider(style=Pack(
1155:             padding=(0, 10)
1156:         )))
1157: 
1158:         # Help section
1159:         help_box = toga.Box(style=Pack(
1160:             direction=COLUMN,
1161:             padding=(10, 0, 20, 0)
1162:         ))
1163: 
1164:         help_title = toga.Label(
1165:             "How to Use",
1166:             style=Pack(
1167:                 font_size=18,
1168:                 font_weight="bold",
1169:                 color=self.colors['text'],
1170:                 padding_bottom=10
1171:             )
1172:         )
1173:         help_box.add(help_title)
1174: 
1175:         # Help content
1176:         help_sections = [
1177:             ("Simulation Modes", [
1178:                 "Typing Only: Simulates keyboard typing from a code file",
1179:                 "Tab Switching Only: Simulates switching between application windows",
1180:                 "Hybrid: Combines typing and application switching",
1181:                 "Mouse and Command+Tab: Simulates mouse movements and Command+Tab switching"
1182:             ]),
1183:             ("File Selection", [
1184:                 "Use the 'Choose File' button to select a .txt file for typing simulation",
1185:                 "If no file is selected, default files from resources/code directory will be used"
1186:             ]),
1187:             ("Configuration", [
1188:                 "Adjust typing speed, language formatting, and other settings in the Configuration tab",
1189:                 "Application targets for switching can be configured in applications.json"
1190:             ]),
1191:             ("Keyboard Shortcuts", [
1192:                 "⌘+S: Start Simulation",
1193:                 "⌘+X: Stop Simulation"
1194:             ])
1195:         ]
1196: 
1197:         for section_title, items in help_sections:
1198:             section_label = toga.Label(
1199:                 section_title,
1200:                 style=Pack(
1201:                     font_size=16,
1202:                     font_weight="bold",
1203:                     color=self.colors['text'],
1204:                     padding=(10, 0, 5, 0)
1205:                 )
1206:             )
1207:             help_box.add(section_label)
1208: 
1209:             for item in items:
1210:                 item_label = toga.Label(
1211:                     "• " + item,
1212:                     style=Pack(
1213:                         color=self.colors['text'],
1214:                         padding=(0, 0, 5, 15)
1215:                     )
1216:                 )
1217:                 help_box.add(item_label)
1218: 
1219:         about_content.add(help_box)
1220: 
1221:         # Add the about content to the scroll container
1222:         scroll_container.content = about_content
1223:         content_card.add(scroll_container)
1224: 
1225:         # Add content card to the view
1226:         about_view.add(content_card)
1227: 
1228:         return about_view
1229: 
1230:     def load_configuration_values(self):
1231: 
1232:         try:
1233:             # Get configuration path
1234:             config_path = self.action_simulator._get_config_path()
1235: 
1236:             # Read configuration file
1237:             with open(config_path, 'r') as f:
1238:                 config = json.load(f)
1239: 
1240:             # Set code configuration values
1241:             code_config = config.get('code', {})
1242:             self.language_input.value = code_config.get('language', 'python')
1243:             self.indent_input.value = code_config.get('indent_size', 4)
1244:             self.max_line_input.value = code_config.get('max_line_length', 80)
1245: 
1246:             # Set typing speed configuration values
1247:             typing_config = config.get('typing_speed', {})
1248:             self.min_speed_input.value = typing_config.get('min', 0.03)
1249:             self.max_speed_input.value = typing_config.get('max', 0.07)
1250:             self.mistake_input.value = typing_config.get('mistake_rate', 0.07)
1251: 
1252:             logger.info("Configuration values loaded successfully")
1253:         except Exception as e:
1254:             logger.error(f"Error loading configuration values: {e}")
1255:             self.console.value = f"Error loading configuration: {e}\n"
1256: 
1257:     async def save_configuration_direct(self, widget):
1258: 
1259:         try:
1260:             # Get configuration path
1261:             config_path = self.action_simulator._get_config_path()
1262: 
1263:             # Read current configuration
1264:             with open(config_path, 'r') as f:
1265:                 config = json.load(f)
1266: 
1267:             # Update code configuration
1268:             if 'code' not in config:
1269:                 config['code'] = {}
1270: 
1271:             config['code']['language'] = self.language_input.value
1272:             config['code']['indent_size'] = self.indent_input.value
1273:             config['code']['max_line_length'] = self.max_line_input.value
1274: 
1275:             # Update typing speed configuration
1276:             if 'typing_speed' not in config:
1277:                 config['typing_speed'] = {}
1278: 
1279:             config['typing_speed']['min'] = self.min_speed_input.value
1280:             config['typing_speed']['max'] = self.max_speed_input.value
1281:             config['typing_speed']['mistake_rate'] = self.mistake_input.value
1282: 
1283:             # Preserve line_break if it exists
1284:             if 'line_break' not in config['typing_speed']:
1285:                 config['typing_speed']['line_break'] = [0.5, 1.0]
1286: 
1287:             # Write updated configuration
1288:             with open(config_path, 'w') as f:
1289:                 json.dump(config, f, indent=4)
1290: 
1291:             # Reload configuration in action simulator
1292:             self.action_simulator.config = self.action_simulator._load_config()
1293:             self.action_simulator._setup_from_config()
1294: 
1295:             # Show success message
1296:             self.console.value = "✅ Configuration saved and reloaded successfully.\n"
1297:             self.status_label.text = "Configuration saved"
1298:             logger.info("Configuration updated successfully")
1299: 
1300:         except Exception as e:
1301:             self.console.value = f"❌ Error saving configuration: {e}\n"
1302:             logger.error(f"Error saving configuration: {e}")
1303: 
1304:     def setup_components(self):
1305: 
1306:         self.action_simulator = ActionSimulator(self.console, self)
1307:         self.key_handler = GlobalKeyHandler(self, self.action_simulator)
1308:         self.simulation_task = None
1309: 
1310:         # Now that ActionSimulator is initialized, we can load configuration values
1311:         self.load_configuration_values()
1312: 
1313:     async def choose_file(self, widget):
1314: 
1315:         try:
1316:             dialog = toga.OpenFileDialog(
1317:                 title="Select a Code File",
1318:                 file_types=["txt"]
1319:             )
1320:             file_path = await self.main_window.dialog(dialog)
1321: 
1322:             # Handle the file_path based on its type
1323:             if file_path:
1324:                 # Convert PosixPath to string if needed
1325:                 if hasattr(file_path, 'resolve'):  # It's a Path object
1326:                     self.selected_file = str(file_path.resolve())
1327:                 elif isinstance(file_path, list) and file_path:  # It's a list of paths
1328:                     self.selected_file = str(file_path[0])
1329:                 else:  # It's already a string
1330:                     self.selected_file = str(file_path)
1331: 
1332:                 filename = os.path.basename(self.selected_file)
1333:                 self.file_display.text = f"Selected: {filename}"
1334:                 logger.info(f"Selected file: {self.selected_file}")
1335:                 self.status_label.text = f"File selected: {filename}"
1336:             else:
1337:                 self.selected_file = None
1338:                 self.file_display.text = "Using default resources/code files"
1339:                 logger.info("No file selected; using default.")
1340:                 self.status_label.text = "Using default files"
1341:         except Exception as e:
1342:             self.console.value += f"Error selecting file: {str(e)}\n"
1343:             logger.error(f"Error in choose_file: {e}")
1344:             self.selected_file = None
1345:             self.file_display.text = "Using default resources/code files"
1346: 
1347:     async def start_simulation(self, widget):
1348: 
1349:         if not self.action_simulator.loop_flag:
1350:             try:
1351:                 self.console.value = "🚀 Starting simulation...\n"
1352:                 self.update_button_states(running=True)
1353:                 self.action_simulator.loop_flag = True
1354:                 self.status_label.text = "Simulation running"
1355: 
1356:                 # Get the selected simulation mode
1357:                 selected_mode = self.mode_selector.value
1358:                 self.action_simulator.simulation_mode = selected_mode
1359:                 self.console.value += f"▶️ Mode: {selected_mode}\n"
1360: 
1361:                 # Determine which file to use based on the selected mode and whether a file was chosen
1362:                 file_to_use = None
1363:                 if selected_mode in ["Typing Only", "Hybrid"]:
1364:                     if self.selected_file and os.path.exists(self.selected_file):
1365:                         file_to_use = self.selected_file
1366:                         filename = os.path.basename(file_to_use)
1367:                         self.console.value += f"📄 Using selected file: {filename}\n"
1368:                         logger.info(f"Using selected file: {file_to_use}")
1369:                     else:
1370:                         self.console.value += "📄 No valid file selected. Using default code samples\n"
1371:                         logger.info("No valid file selected, using default code samples")
1372:                 else:
1373:                     self.console.value += "📄 File selection not applicable for this mode\n"
1374:                     logger.info("File selection not applicable for this mode")
1375: 
1376:                 # Start the simulation task
1377:                 if not self.simulation_task:
1378:                     self.simulation_task = asyncio.create_task(self.run_continuous_simulation(file_to_use))
1379:                 logger.info("Simulation started successfully.")
1380:             except Exception as e:
1381:                 logger.error(f"Error starting simulation: {e}")
1382:                 await self.stop_simulation(widget)
1383: 
1384:     async def run_continuous_simulation(self, file_to_use: Optional[str]):
1385: 
1386:         try:
1387:             while self.action_simulator.loop_flag:
1388:                 # Determine which file to use
1389:                 if file_to_use and os.path.exists(file_to_use):
1390:                     next_file = file_to_use
1391:                     logger.debug(f"Using provided file: {next_file}")
1392:                 else:
1393:                     next_file = self.action_simulator.get_next_code_file()
1394:                     logger.debug(f"Using default file: {next_file}")
1395: 
1396:                 if not next_file:
1397:                     self.console.value += "❌ No code files found to simulate typing.\n"
1398:                     await asyncio.sleep(2)
1399:                     continue
1400: 
1401:                 # Calculate typing time if applicable
1402:                 if self.action_simulator.simulation_mode in ["Typing Only", "Hybrid"]:
1403:                     await self.action_simulator.calculate_typing_time(next_file)
1404: 
1405:                 # Execute the simulation based on the selected mode
1406:                 if self.action_simulator.simulation_mode == "Typing Only":
1407:                     self.console.value += "⌨️ Simulating typing...\n"
1408:                     await self.action_simulator.simulate_typing(next_file)
1409:                 elif self.action_simulator.simulation_mode == "Tab Switching Only":
1410:                     self.console.value += "🔄 Switching between applications...\n"
1411:                     self.action_simulator.switch_window()
1412:                     await asyncio.sleep(2)
1413:                 elif self.action_simulator.simulation_mode == "Hybrid":
1414:                     self.console.value += "⌨️ Simulating typing...\n"
1415:                     await self.action_simulator.simulate_typing(next_file)
1416:                     self.console.value += "🔄 Switching between applications...\n"
1417:                     self.action_simulator.switch_window()
1418:                     await asyncio.sleep(2)
1419:                 elif self.action_simulator.simulation_mode == "Mouse and Command+Tab":
1420:                     # Use the dedicated method for this simulation mode
1421:                     await self.action_simulator.simulate_mouse_and_command_tab(duration=15)  # Run for 15 seconds
1422: 
1423:                 filename = os.path.basename(next_file)
1424:                 self.console.value += f"\n✅ Finished simulating file: {filename}\n"
1425:                 self.console.value += "🔄 Cycle completed. Restarting...\n\n"
1426:                 self.status_label.text = "Cycle completed"
1427:                 await asyncio.sleep(2)
1428:         except asyncio.CancelledError:
1429:             self.console.value += "⏹️ Simulation task cancelled.\n"
1430:             self.status_label.text = "Simulation cancelled"
1431:         except Exception as e:
1432:             self.console.value += f"❌ Error during simulation: {str(e)}\n"
1433:             self.status_label.text = "Error in simulation"
1434:             logger.error(f"Error in continuous simulation: {e}")
1435:             await self.stop_simulation(None)
1436: 
1437:     async def stop_simulation(self, widget):
1438: 
1439:         if self.action_simulator.loop_flag:
1440:             try:
1441:                 self.console.value += "⏹️ Stopping simulation...\n"
1442:                 self.action_simulator.loop_flag = False
1443:                 self.update_button_states(running=False)
1444:                 self.status_label.text = "Simulation stopped"
1445:                 if self.simulation_task:
1446:                     self.simulation_task.cancel()
1447:                     self.simulation_task = None
1448:                 logger.info("Simulation stopped successfully.")
1449:             except Exception as e:
1450:                 logger.error(f"Error stopping simulation: {e}")
1451: 
1452:     def update_button_states(self, running: bool):
1453: 
1454:         self.start_button.enabled = not running
1455:         self.stop_button.enabled = running
1456: 
1457: 
1458: def main():
1459:     return CodeSimulator()
```

## File: src/codesimulator/config.py
```python
  1: import sys
  2: import json
  3: import os
  4: 
  5: from typing import Dict, List
  6: from .logging_config import logger
  7: 
  8: DEFAULT_APPS = {
  9:     'darwin': {
 10:         'applications': [
 11:             {
 12:                 'name': 'Google Chrome',
 13:                 'process_name': 'Google Chrome',
 14:                 'bundle_id': 'com.google.Chrome',
 15:             },
 16:             {
 17:                 'name': 'IntelliJ IDEA',
 18:                 'process_name': 'IntelliJ IDEA',
 19:                 'bundle_id': 'com.jetbrains.intellij',
 20:             },
 21:             {
 22:                 'name': 'Sublime Text',
 23:                 'process_name': 'Sublime Text',
 24:                 'bundle_id': 'com.sublimetext.4',
 25:             }
 26:         ]
 27:     },
 28:     'win32': {
 29:         'applications': [
 30:             {
 31:                 'name': 'Google Chrome',
 32:                 'process_name': 'chrome.exe',
 33:                 'window_class': 'Chrome_WidgetWin_1',
 34:             },
 35:             {
 36:                 'name': 'IntelliJ IDEA',
 37:                 'process_name': 'idea64.exe',
 38:                 'window_class': 'SunAwtFrame',
 39:             },
 40:             {
 41:                 'name': 'Sublime Text',
 42:                 'process_name': 'sublime_text.exe',
 43:                 'window_class': 'PX_WINDOW_CLASS',
 44:             }
 45:         ]
 46:     },
 47:     'linux': {
 48:         'applications': [
 49:             {
 50:                 'name': 'Google Chrome',
 51:                 'process_name': 'chrome',
 52:                 'window_class': 'Google-chrome',
 53:             },
 54:             {
 55:                 'name': 'IntelliJ IDEA',
 56:                 'process_name': 'idea.sh',
 57:                 'window_class': 'jetbrains-idea',
 58:             },
 59:             {
 60:                 'name': 'Sublime Text',
 61:                 'process_name': 'sublime_text',
 62:                 'window_class': 'sublime_text',
 63:             }
 64:         ]
 65:     }
 66: }
 67: 
 68: 
 69: class AppConfig:
 70:     def __init__(self, app=None):
 71:         self.app = app
 72:         self.config_path = self._get_config_path()
 73:         self.platform = sys.platform
 74:         self.apps = self._load_config()
 75: 
 76:     def _get_config_path(self) -> str:
 77: 
 78:         from .path_utils import get_resource_path
 79:         return get_resource_path(self.app, 'applications.json')
 80: 
 81:     def _load_config(self) -> Dict:
 82: 
 83:         try:
 84:             if os.path.exists(self.config_path):
 85:                 with open(self.config_path, 'r') as f:
 86:                     config = json.load(f)
 87:                     if self.platform in config:
 88:                         return config
 89: 
 90: 
 91:             return self._create_default_config()
 92:         except Exception as e:
 93:             logger.error(f"Error loading config3: {e}")
 94:             return self._create_default_config()
 95: 
 96:     def _create_default_config(self) -> Dict:
 97: 
 98:         config = DEFAULT_APPS
 99:         try:
100:             with open(self.config_path, 'w') as f:
101:                 json.dump(config, f, indent=4)
102:         except Exception as e:
103:             logger.error(f"Error saving default config: {e}")
104:         return config
105: 
106:     def get_applications(self) -> List[Dict]:
107: 
108:         return self.apps.get(self.platform, {}).get('applications', [])
109: 
110:     def add_application(self, app_info: Dict) -> bool:
111: 
112:         try:
113:             if self.platform not in self.apps:
114:                 self.apps[self.platform] = {'applications': []}
115: 
116:             self.apps[self.platform]['applications'].append(app_info)
117: 
118:             with open(self.config_path, 'w') as f:
119:                 json.dump(self.apps, f, indent=4)
120:             return True
121:         except Exception as e:
122:             logger.error(f"Error adding application: {e}")
123:             return False
124: 
125:     def remove_application(self, app_name: str) -> bool:
126: 
127:         try:
128:             if self.platform in self.apps:
129:                 apps = self.apps[self.platform]['applications']
130:                 self.apps[self.platform]['applications'] = [
131:                     app for app in apps if app['name'] != app_name
132:                 ]
133: 
134:                 with open(self.config_path, 'w') as f:
135:                     json.dump(self.apps, f, indent=4)
136:                 return True
137:         except Exception as e:
138:             logger.error(f"Error removing application: {e}")
139:         return False
```

## File: src/codesimulator/key_handler.py
```python
 1: import asyncio
 2: from platform import system
 3: from .logging_config import logger
 4: 
 5: 
 6: class GlobalKeyHandler:
 7: 
 8: 
 9:     def __init__(self, app, action_simulator):
10: 
11:         self.app = app
12:         self.action_simulator = action_simulator
13:         self.platform = system()
14:         self._setup_platform_handler()
15: 
16:     def _setup_platform_handler(self):
17: 
18:         try:
19:             if self.platform == 'Darwin':
20:                 self._setup_macos_handler()
21:             else:
22:                 logger.info(f"Using default key handling for platform: {self.platform}")
23:         except Exception as e:
24:             logger.error(f"Error setting up key handler: {e}")
25: 
26:     def _setup_macos_handler(self):
27: 
28:         try:
29:             from AppKit import NSEvent, NSKeyDownMask
30: 
31:             def handle_ns_event(event):
32:                 if event.type() == NSKeyDownMask:
33:                     key = event.charactersIgnoringModifiers()
34:                     if key in ["+", "="]:
35:                         self.toggle_simulation()
36:                     elif key == "-":
37:                         self.app.stop_simulation(None)
38: 
39:             NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
40:                 NSKeyDownMask,
41:                 handle_ns_event
42:             )
43:             logger.info("MacOS key handler initialized successfully")
44:         except Exception as e:
45:             logger.error(f"Failed to initialize MacOS key handler: {e}")
46: 
47:     async def run(self):
48: 
49:         try:
50:             logger.info("Global key handler started")
51:             while True:
52:                 await asyncio.sleep(0.1)
53:         except asyncio.CancelledError:
54:             logger.info("Key handler task cancelled")
55:         except Exception as e:
56:             logger.error(f"Error in key handler: {e}")
57: 
58:     def toggle_simulation(self):
59: 
60:         try:
61:             if self.action_simulator.loop_flag:
62:                 self.app.stop_simulation(None)
63:             else:
64:                 self.app.start_simulation(None)
65:         except Exception as e:
66:             logger.error(f"Error toggling simulation: {e}")
67: 
68:     def cleanup(self):
69: 
70:         try:
71:             if self.platform == 'Darwin':
72: 
73:                 pass
74:             logger.info("Key handler cleanup completed")
75:         except Exception as e:
76:             logger.error(f"Error during key handler cleanup: {e}")
```

## File: src/codesimulator/language_formatter.py
```python
  1: import re
  2: from .logging_config import logger
  3: 
  4: 
  5: class LanguageFormatter:
  6: 
  7: 
  8:     def __init__(self, indent_size=4):
  9:         self.indent_size = indent_size
 10:         self.indent_level = 0
 11:         self.indent_style = " " * indent_size
 12: 
 13:     def format_line(self, line: str) -> str:
 14: 
 15:         line = line.strip()
 16: 
 17: 
 18:         if line.endswith("{") or line.endswith("("):
 19:             indented_line = self.indent_style * self.indent_level + line
 20:             self.indent_level += 1
 21:         elif line.startswith("}") or line.startswith(")"):
 22:             self.indent_level = max(0, self.indent_level - 1)
 23:             indented_line = self.indent_style * self.indent_level + line
 24:         else:
 25:             indented_line = self.indent_style * self.indent_level + line
 26: 
 27:         return indented_line
 28: 
 29: 
 30: class JavaFormatter(LanguageFormatter):
 31: 
 32: 
 33:     def format_line(self, line: str) -> str:
 34: 
 35:         line = super().format_line(line)
 36: 
 37: 
 38: 
 39:         line = re.sub(r"(?<=\w),(?=\w)", ", ", line)
 40: 
 41: 
 42:         if line.endswith("{"):
 43:             indented_line = self.indent_style * self.indent_level + line
 44:             self.indent_level += 1
 45:         elif line.startswith("}"):
 46:             self.indent_level = max(0, self.indent_level - 1)
 47:             indented_line = self.indent_style * self.indent_level + line
 48:         elif (
 49:                 line.startswith("if")
 50:                 or line.startswith("else")
 51:                 or line.startswith("for")
 52:                 or line.startswith("while")
 53:         ):
 54:             indented_line = self.indent_style * self.indent_level + line
 55:             self.indent_level += 1
 56:         else:
 57:             indented_line = self.indent_style * self.indent_level + line
 58: 
 59:         return indented_line
 60: 
 61: 
 62: class PythonFormatter(LanguageFormatter):
 63: 
 64: 
 65:     def format_line(self, line: str) -> str:
 66: 
 67:         line = super().format_line(line)
 68: 
 69: 
 70: 
 71:         if re.match(
 72:                 r"^(if|elif|else|for|while|try|except|finally|def|class)\b.*[^:]$", line
 73:         ):
 74:             line = line + ":"
 75: 
 76:         return line
 77: 
 78: 
 79: class PHPFormatter(LanguageFormatter):
 80: 
 81: 
 82:     def format_line(self, line: str) -> str:
 83: 
 84:         line = super().format_line(line)
 85: 
 86: 
 87: 
 88:         line = re.sub(r"(\s*)(=|!=|==|<=|>=|<|>|\+|-|\*|\/|%|&&|\|\|)(\s*)", r" \1 ", line)
 89: 
 90: 
 91:         line = re.sub(r"(,)(?=\S)", r"$1 ", line)
 92: 
 93: 
 94:         line = re.sub(r"\s+\)", ")", line)
 95: 
 96: 
 97:         if line.endswith("{"):
 98:             indented_line = self.indent_style * self.indent_level + line
 99:             self.indent_level += 1
100:         elif line.startswith("}"):
101:             self.indent_level = max(0, self.indent_level - 1)
102:             indented_line = self.indent_style * self.indent_level + line
103:         elif (
104:                 line.startswith("if")
105:                 or line.startswith("else")
106:                 or line.startswith("elseif")
107:                 or line.startswith("for")
108:                 or line.startswith("foreach")
109:                 or line.startswith("while")
110:                 or line.startswith("function")
111:         ):
112:             indented_line = self.indent_style * self.indent_level + line
113:             self.indent_level += 1
114:         else:
115:             indented_line = self.indent_style * self.indent_level + line
116: 
117:         return indented_line
118: 
119: 
120: 
121: 
122: 
123: class FormatterFactory:
124: 
125: 
126:     @staticmethod
127:     def create_formatter(language: str, indent_size: int = 4) -> LanguageFormatter:
128: 
129:         if language == "java":
130:             return JavaFormatter(indent_size)
131:         elif language == "python":
132:             return PythonFormatter(indent_size)
133:         elif language == "php":
134:             return PHPFormatter(indent_size)
135: 
136:         else:
137:             logger.warning(
138:                 f"No specific formatter found for {language}. Using default formatter."
139:             )
140:             return LanguageFormatter(indent_size)
```

## File: src/codesimulator/logging_config.py
```python
 1: import logging
 2: import logging.handlers
 3: import os
 4: import sys
 5: import tempfile
 6: import platform
 7: 
 8: 
 9: logger = logging.getLogger('codesimulator')
10: logger.setLevel(logging.DEBUG)
11: 
12: 
13: console_handler = logging.StreamHandler()
14: console_handler.setLevel(logging.INFO)
15: formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
16: console_handler.setFormatter(formatter)
17: logger.addHandler(console_handler)
18: 
19: 
20: _file_logging_initialized = False
21: 
22: 
23: def get_log_path():
24: 
25:     try:
26: 
27:         if platform.system() == "Darwin":
28:             # This directory should always be writable for the current user on macOS
29:             log_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')
30:         else:
31:             # For other platforms
32:             log_dir = os.path.join(tempfile.gettempdir(), 'CodeSimulator', 'logs')
33: 
34:         # Ensure directory exists
35:         os.makedirs(log_dir, exist_ok=True)
36: 
37:         # Return full path
38:         return os.path.join(log_dir, 'codesimulator.log')
39:     except Exception:
40:         # Ultimate fallback - use temp directory
41:         return os.path.join(tempfile.gettempdir(), 'codesimulator.log')
42: 
43: 
44: def setup_file_logging():
45: 
46:     global _file_logging_initialized
47: 
48: 
49:     if _file_logging_initialized:
50:         return
51: 
52:     try:
53: 
54:         log_file_path = get_log_path()
55: 
56: 
57:         file_handler = logging.handlers.RotatingFileHandler(
58:             log_file_path, maxBytes=5 * 1024 * 1024, backupCount=2
59:         )
60:         file_handler.setLevel(logging.DEBUG)
61:         file_handler.setFormatter(formatter)
62: 
63: 
64:         logger.addHandler(file_handler)
65: 
66: 
67:         _file_logging_initialized = True
68: 
69: 
70:         logger.info(f"File logging initialized at: {log_file_path}")
71: 
72:     except Exception as e:
73: 
74:         logger.error(f"Failed to set up file logging: {e}")
75: 
76: 
77: 
78: setup_file_logging()
```

## File: src/codesimulator/mouse.py
```python
 1: import asyncio
 2: import random
 3: import pyautogui
 4: from typing import Optional, Tuple
 5: from .logging_config import logger
 6: 
 7: 
 8: class MouseController:
 9: 
10: 
11:     def __init__(self):
12: 
13:         self.is_active = False
14:         self.screen_width, self.screen_height = pyautogui.size()
15:         self.movement_task: Optional[asyncio.Task] = None
16: 
17:     async def start_random_movement(self,
18:                                     min_interval: float = 5.0,
19:                                     max_interval: float = 15.0,
20:                                     excluded_zone: Optional[Tuple[int, int, int, int]] = None):
21: 
22:         self.is_active = True
23: 
24:         while self.is_active:
25:             try:
26: 
27:                 x = random.randint(0, self.screen_width)
28:                 y = random.randint(0, self.screen_height)
29: 
30: 
31:                 if excluded_zone:
32:                     x1, y1, x2, y2 = excluded_zone
33:                     if x1 <= x <= x2 and y1 <= y <= y2:
34:                         continue
35: 
36: 
37:                 current_x, current_y = pyautogui.position()
38:                 distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
39:                 duration = min(2.0, distance / 1000)
40: 
41: 
42:                 pyautogui.moveTo(x, y, duration=duration)
43:                 logger.debug(f"Moved mouse to ({x}, {y})")
44: 
45: 
46:                 wait_time = random.uniform(min_interval, max_interval)
47:                 await asyncio.sleep(wait_time)
48: 
49:             except Exception as e:
50:                 logger.error(f"Error in mouse movement: {e}")
51:                 await asyncio.sleep(1)
52: 
53:     def start(self,
54:               min_interval: float = 5.0,
55:               max_interval: float = 15.0,
56:               excluded_zone: Optional[Tuple[int, int, int, int]] = None):
57: 
58:         if self.movement_task and not self.movement_task.done():
59:             return
60: 
61:         self.movement_task = asyncio.create_task(
62:             self.start_random_movement(min_interval, max_interval, excluded_zone)
63:         )
64: 
65:     def stop(self):
66: 
67:         self.is_active = False
68:         if self.movement_task:
69:             self.movement_task.cancel()
70:             self.movement_task = None
```

## File: src/codesimulator/path_utils.py
```python
  1: import os
  2: import sys
  3: import tempfile
  4: import platform
  5: from .logging_config import logger
  6: 
  7: 
  8: def is_packaged():
  9: 
 10:     return getattr(sys, 'frozen', False)
 11: 
 12: 
 13: def get_resource_path(app=None, *paths):
 14: 
 15:     try:
 16: 
 17:         if app and hasattr(app, 'paths') and hasattr(app.paths, 'resources'):
 18:             base_path = app.paths.resources
 19:             logger.debug(f"Using Toga resource path: {base_path}")
 20:         else:
 21:             # Fallback based on environment
 22:             if is_packaged():
 23:                 # Packaged app - path depends on platform
 24:                 if platform.system() == 'Darwin':  # macOS
 25:                     base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))),
 26:                                              'Resources')
 27:                 elif platform.system() == 'Windows':
 28:                     base_path = os.path.join(os.path.dirname(sys.executable), 'app', 'resources')
 29:                 else:  # Linux and others
 30:                     base_path = os.path.join(os.path.dirname(sys.executable), 'resources')
 31:                 logger.debug(f"Using packaged resource path: {base_path}")
 32:             else:
 33:                 # Development environment
 34:                 base_path = os.path.join(os.path.dirname(__file__), 'resources')
 35:                 logger.debug(f"Using development resource path: {base_path}")
 36: 
 37:         full_path = os.path.join(base_path, *paths)
 38:         logger.debug(f"Full resource path: {full_path}")
 39:         return full_path
 40:     except Exception as e:
 41:         logger.error(f"Error getting resource path: {e}")
 42:         # Last resort fallback
 43:         return os.path.join(os.path.dirname(__file__), 'resources', *paths)
 44: 
 45: 
 46: def get_log_path():
 47: 
 48:     if is_packaged():
 49:         # Use system temp directory for packaged app
 50:         log_dir = tempfile.gettempdir()
 51:     else:
 52:         # Use resources directory in development
 53:         log_dir = os.path.join(os.path.dirname(__file__), 'resources')
 54: 
 55:     if not os.path.exists(log_dir):
 56:         try:
 57:             os.makedirs(log_dir)
 58:         except Exception:
 59:             pass
 60: 
 61:     return os.path.join(log_dir, 'codesimulator.log')
 62: 
 63: 
 64: def log_environment_info():
 65: 
 66:     info = {
 67:         "Platform": platform.system(),
 68:         "Python Version": sys.version,
 69:         "Packaged App": is_packaged(),
 70:         "Executable Path": sys.executable,
 71:         "Current Directory": os.getcwd(),
 72:         "Module Path": os.path.dirname(__file__),
 73:         "Resource Path Example": get_resource_path(None, 'config.json')
 74:     }
 75: 
 76:     for key, value in info.items():
 77:         logger.info(f"{key}: {value}")
 78: 
 79: 
 80: def get_log_path():
 81: 
 82:     try:
 83:         if is_packaged():
 84:             # Use a more accessible location for packaged app
 85:             if platform.system() == "Windows":
 86:                 log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), "CodeSimulator", "logs")
 87:             elif platform.system() == "Darwin":  # macOS
 88:                 log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs", "CodeSimulator")
 89:             else:  # Linux and others
 90:                 log_dir = os.path.join(os.path.expanduser("~"), ".codesimulator", "logs")
 91:         else:
 92:             # Use resources directory in development
 93:             log_dir = os.path.join(os.path.dirname(__file__), 'resources')
 94: 
 95:         # Create directory if it doesn't exist
 96:         if not os.path.exists(log_dir):
 97:             os.makedirs(log_dir)
 98: 
 99:         return os.path.join(log_dir, 'codesimulator.log')
100:     except Exception as e:
101: 
102:         import tempfile
103:         return os.path.join(tempfile.gettempdir(), 'codesimulator.log')
```

## File: src/codesimulator.dist-info/INSTALLER
```
1: briefcase
```

## File: src/codesimulator.dist-info/METADATA
```
 1: Metadata-Version: 2.1
 2: Briefcase-Version: 0.3.14
 3: Name: codesimulator
 4: Formal-Name: Code Simulator
 5: App-ID: com.rylxes.code-simulator.codesimulator
 6: Version: 0.0.1
 7: Home-page: https://code-simulator.rylxes.com/codesimulator
 8: Download-URL: https://code-simulator.rylxes.com/codesimulator
 9: Author: rylxes
10: Author-email: rylxes@gmail.com
11: Summary: My first application
```

## File: src/codesimulator.dist-info/top_level.txt
```
1: codesimulator
```

## File: src/codesimulator.dist-info/WHEEL
```
1: Wheel-Version: 1.0
2: Root-Is-Purelib: true
3: Generator: briefcase (0.3.14)
4: Tag: py3-none-any
```

## File: CHANGELOG
```
1: # Code Simulator Release Notes
2: 
3: ## 0.0.1 (12 Jan 2025)
4: 
5: * Initial release
```

## File: LICENSE
```
 1: Copyright (c) 2025, rylxes
 2: All rights reserved.
 3: 
 4: Redistribution and use in source and binary forms, with or without modification,
 5: are permitted provided that the following conditions are met:
 6: 
 7: * Redistributions of source code must retain the above copyright notice, this
 8:   list of conditions and the following disclaimer.
 9: 
10: * Redistributions in binary form must reproduce the above copyright notice, this
11:   list of conditions and the following disclaimer in the documentation and/or
12:   other materials provided with the distribution.
13: 
14: * Neither the name of the copyright holder nor the names of its
15:   contributors may be used to endorse or promote products derived from this
16:   software without specific prior written permission.
17: 
18: THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
19: ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
20: WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
21: IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
22: INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
23: BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
24: DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
25: OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
26: OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
27: OF THE POSSIBILITY OF SUCH DAMAGE.
```

## File: pyproject.toml
```toml
  1: # This project was generated with 0.3.20 using template: https://github.com/beeware/briefcase-template@v0.3.20
  2: [tool.briefcase]
  3: project_name = "Code Simulator"
  4: bundle = "com.rylxes.code-simulator"
  5: version = "0.0.1"
  6: url = "https://code-simulator.rylxes.com/codesimulator"
  7: license.file = "LICENSE"
  8: author = "rylxes"
  9: author_email = "rylxes@gmail.com"
 10: 
 11: [tool.briefcase.app.codesimulator]
 12: formal_name = "Code Simulator"
 13: description = "My first application"
 14: long_description = """More details about the app should go here.
 15: """
 16: sources = [
 17:     "src/codesimulator",
 18: ]
 19: test_sources = [
 20:     "tests",
 21: ]
 22: 
 23: requires = [
 24:     "pyautogui>=0.9.53",
 25:     "PyQt5>=5.15"
 26: ]
 27: test_requires = [
 28:     "pytest",
 29: ]
 30: 
 31: resources = [
 32:     "src/codesimulator/resources",
 33: ]
 34: 
 35: [tool.briefcase.app.codesimulator.macOS]
 36: universal_build = true
 37: requires = [
 38:     "toga-cocoa~=0.4.7",
 39:     "std-nslog~=1.0.3",
 40:     "pyautogui>=0.9.53",
 41:     "PyQt5>=5.15"
 42: ]
 43: 
 44: entitlements = [
 45:     "com.apple.security.automation.apple-events",
 46:     "com.apple.security.device.camera",  # if needed
 47:     "com.apple.security.device.audio-input",  # if needed
 48: ]
 49: 
 50: 
 51: [tool.briefcase.app.codesimulator.macOS.info]
 52: NSAppleEventsUsageDescription = "Code Simulator needs to control other applications to perform simulations."
 53: NSAccessibilityUsageDescription = "Code Simulator needs accessibility access to simulate keyboard and mouse inputs."
 54: 
 55: [tool.briefcase.app.codesimulator.linux]
 56: requires = [
 57:     "toga-cocoa~=0.4.7",
 58:     "std-nslog~=1.0.3",
 59:     "pyautogui>=0.9.53",
 60:     "PyQt5>=5.15"
 61: ]
 62: 
 63: [tool.briefcase.app.codesimulator.linux.system.debian]
 64: system_requires = [
 65:     # Needed to compile pycairo wheel
 66:     "libcairo2-dev",
 67:     # Needed to compile PyGObject wheel
 68:     "libgirepository1.0-dev",
 69: ]
 70: 
 71: system_runtime_requires = [
 72:     # Needed to provide GTK and its GI bindings
 73:     "gir1.2-gtk-3.0",
 74:     "libgirepository-1.0-1",
 75:     # Dependencies that GTK looks for at runtime
 76:     "libcanberra-gtk3-module",
 77:     # Needed to provide WebKit2 at runtime
 78:     # Note: Debian 11 and Ubuntu 20.04 require gir1.2-webkit2-4.0 instead
 79:     # "gir1.2-webkit2-4.1",
 80: ]
 81: 
 82: [tool.briefcase.app.codesimulator.linux.system.rhel]
 83: system_requires = [
 84:     # Needed to compile pycairo wheel
 85:     "cairo-gobject-devel",
 86:     # Needed to compile PyGObject wheel
 87:     "gobject-introspection-devel",
 88: ]
 89: 
 90: system_runtime_requires = [
 91:     # Needed to support Python bindings to GTK
 92:     "gobject-introspection",
 93:     # Needed to provide GTK
 94:     "gtk3",
 95:     # Dependencies that GTK looks for at runtime
 96:     "libcanberra-gtk3",
 97:     # Needed to provide WebKit2 at runtime
 98:     # "webkit2gtk3",
 99: ]
100: 
101: [tool.briefcase.app.codesimulator.linux.system.suse]
102: system_requires = [
103:     # Needed to compile pycairo wheel
104:     "cairo-devel",
105:     # Needed to compile PyGObject wheel
106:     "gobject-introspection-devel",
107: ]
108: 
109: system_runtime_requires = [
110:     # Needed to provide GTK
111:     "gtk3",
112:     # Needed to support Python bindings to GTK
113:     "gobject-introspection", "typelib(Gtk) = 3.0",
114:     # Dependencies that GTK looks for at runtime
115:     "libcanberra-gtk3-module",
116:     # Needed to provide WebKit2 at runtime
117:     # "libwebkit2gtk3", "typelib(WebKit2)",
118: ]
119: 
120: [tool.briefcase.app.codesimulator.linux.system.arch]
121: system_requires = [
122:     # Needed to compile pycairo wheel
123:     "cairo",
124:     # Needed to compile PyGObject wheel
125:     "gobject-introspection",
126:     # Runtime dependencies that need to exist so that the
127:     # Arch package passes final validation.
128:     # Needed to provide GTK
129:     "gtk3",
130:     # Dependencies that GTK looks for at runtime
131:     "libcanberra",
132:     # Needed to provide WebKit2
133:     # "webkit2gtk",
134: ]
135: 
136: system_runtime_requires = [
137:     # Needed to provide GTK
138:     "gtk3",
139:     # Needed to provide PyGObject bindings
140:     "gobject-introspection-runtime",
141:     # Dependencies that GTK looks for at runtime
142:     "libcanberra",
143:     # Needed to provide WebKit2 at runtime
144:     # "webkit2gtk",
145: ]
146: 
147: [tool.briefcase.app.codesimulator.linux.appimage]
148: manylinux = "manylinux_2_28"
149: 
150: system_requires = [
151:     # Needed to compile pycairo wheel
152:     "cairo-gobject-devel",
153:     # Needed to compile PyGObject wheel
154:     "gobject-introspection-devel",
155:     # Needed to provide GTK
156:     "gtk3-devel",
157:     # Dependencies that GTK looks for at runtime, that need to be
158:     # in the build environment to be picked up by linuxdeploy
159:     "libcanberra-gtk3",
160:     "PackageKit-gtk3-module",
161:     "gvfs-client",
162: ]
163: 
164: linuxdeploy_plugins = [
165:     "DEPLOY_GTK_VERSION=3 gtk",
166: ]
167: 
168: [tool.briefcase.app.codesimulator.linux.flatpak]
169: flatpak_runtime = "org.gnome.Platform"
170: flatpak_runtime_version = "47"
171: flatpak_sdk = "org.gnome.Sdk"
172: 
173: [tool.briefcase.app.codesimulator.windows]
174: requires = [
175:     "toga-winforms~=0.4.7",
176:     "pyautogui>=0.9.53",
177:     "PyQt5>=5.15"
178: ]
179: 
180: # Mobile deployments
181: [tool.briefcase.app.codesimulator.iOS]
182: requires = [
183:     "toga-iOS~=0.4.7",
184:     "std-nslog~=1.0.3",
185: ]
186: 
187: [tool.briefcase.app.codesimulator.android]
188: requires = [
189:     "toga-android~=0.4.7",
190: ]
191: 
192: base_theme = "Theme.MaterialComponents.Light.DarkActionBar"
193: 
194: build_gradle_dependencies = [
195:     "com.google.android.material:material:1.12.0",
196:     # Needed for DetailedList
197:     # "androidx.swiperefreshlayout:swiperefreshlayout:1.1.0",
198:     # Needed for MapView
199:     # "org.osmdroid:osmdroid-android:6.1.20",
200: ]
201: 
202: # Web deployments
203: [tool.briefcase.app.codesimulator.web]
204: requires = [
205:     "toga-web~=0.4.7",
206:     "pyautogui>=0.9.53",
207:     "PyQt5>=5.15"
208: ]
209: style_framework = "Shoelace v2.3"
```

## File: README.rst
```
1: briefcase package
2:  briefcase dev -r
```
