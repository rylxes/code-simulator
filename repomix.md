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
  4: import sys
  5: import json
  6: from typing import Optional
  7: 
  8: import pyautogui
  9: 
 10: from .app_switcher import AppSwitcher
 11: from .config import AppConfig
 12: from .language_formatter import FormatterFactory
 13: from .logging_config import logger
 14: from .mouse import MouseController
 15: 
 16: 
 17: class ActionSimulator:
 18: 
 19: 
 20:     def __init__(self, text_box, app=None):
 21:         self.text_box = text_box
 22:         self.app = app
 23:         self.loop_flag = False
 24:         self._configure_pyautogui()
 25:         self.app_config = AppConfig(app)
 26:         self.app_switcher = AppSwitcher(self.app_config)
 27:         self.formatter_factory = FormatterFactory()
 28:         self.formatter = None
 29:         self.mouse_controller = MouseController()
 30:         self.simulation_mode = "Hybrid"
 31: 
 32:         self.config = self._load_config()
 33:         self._setup_from_config()
 34: 
 35: 
 36:         self.code_files = self._get_code_files()
 37:         self.current_code_index = 0
 38: 
 39:         self.original_indentations = {}
 40: 
 41:     def _setup_from_config(self):
 42:         try:
 43:             code_config = self.config.get('code', {})
 44:             self.language = code_config.get('language', 'python')
 45:             self.indent_size = code_config.get('indent_size', 4)
 46:             self.max_line_length = code_config.get('max_line_length', 80)
 47:             typing_config = self.config.get('typing_speed', {})
 48:             self.typing_speed = {
 49:                 'min': typing_config.get('min', 0.03),
 50:                 'max': typing_config.get('max', 0.07),
 51:                 'line_break': tuple(typing_config.get('line_break', [0.5, 1.0])),
 52:                 'mistake_rate': typing_config.get('mistake_rate', 0.07)
 53:             }
 54:             logger.info("Successfully configured simulation settings")
 55:         except Exception as e:
 56:             logger.error(f"Error setting up configuration: {e}")
 57:             self._setup_default_config()
 58: 
 59:     def _setup_default_config(self):
 60:         logger.warning("Using default configuration settings")
 61:         self.language = 'python'
 62:         self.indent_size = 4
 63:         self.max_line_length = 80
 64:         self.typing_speed = {
 65:             'min': 0.03,
 66:             'max': 0.07,
 67:             'line_break': (0.5, 1.0),
 68:             'mistake_rate': 0.07,
 69:         }
 70: 
 71:     def _get_config_path(self) -> str:
 72:         from .path_utils import get_resource_path
 73:         config_path = get_resource_path(self.app, 'config.json')
 74:         if not os.path.exists(config_path):
 75:             logger.error(f"Config file not found at {config_path}")
 76:             raise FileNotFoundError(f"Config file not found at {config_path}")
 77:         return config_path
 78: 
 79:     def _get_code_files(self) -> list:
 80: 
 81:         from .path_utils import get_resource_path
 82:         code_dir = get_resource_path(self.app, 'code')
 83:         if os.path.isdir(code_dir):
 84:             files = [os.path.join(code_dir, f) for f in os.listdir(code_dir) if f.endswith(".txt")]
 85:             if not files:
 86:                 logger.warning(f"No .txt files found in {code_dir}")
 87:             return files
 88:         else:
 89:             logger.warning(f"Code directory not found: {code_dir}")
 90:             return []
 91: 
 92:     def _load_config(self) -> dict:
 93:         try:
 94:             with open(self._get_config_path(), 'r') as f:
 95:                 config = json.load(f)
 96:                 logger.info("Successfully loaded configuration")
 97:                 return config
 98:         except Exception as e:
 99:             logger.error(f"Error loading config: {e}")
100:             raise
101: 
102:     def load_config(self):
103:         try:
104:             config_path = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')
105:             logger.info(f"Loading config from: {config_path}")
106:             with open(config_path, "r") as f:
107:                 config = json.load(f)
108:                 code_config = config.get('code', {})
109:                 self.language = code_config.get("language", "unknown")
110:                 self.indent_size = code_config.get("indent_size", 4)
111:                 self.max_line_length = code_config.get("max_line_length", 80)
112:         except Exception as e:
113:             logger.error(f"Error loading config: {e}")
114:             self.language = "unknown"
115:             self.indent_size = 4
116:             self.max_line_length = 80
117: 
118:     def _configure_pyautogui(self):
119:         try:
120:             import pyautogui
121:             pyautogui.FAILSAFE = True
122:             pyautogui.PAUSE = 0.1
123:             logger.info(f"PyAutoGUI initialized. Screen size: {pyautogui.size()}")
124:         except Exception as e:
125:             logger.error(f"Failed to initialize PyAutoGUI: {e}")
126:             self.text_box.value += f"⚠️ Warning: Failed to initialize PyAutoGUI: {e}\n"
127: 
128: 
129: 
130:     def get_next_code_file(self) -> Optional[str]:
131: 
132:         if self.code_files:
133:             file_path = self.code_files[self.current_code_index]
134:             self.current_code_index = (self.current_code_index + 1) % len(self.code_files)
135:             return file_path
136:         return None
137: 
138:     def _split_file_into_chunks(self, file_path: str, chunk_size: int = 50) -> list:
139: 
140:         with open(file_path, "r") as f:
141:             lines = f.readlines()
142:         if len(lines) <= chunk_size:
143:             return [lines]
144:         chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
145:         logger.info(f"Split file {file_path} into {len(chunks)} chunks")
146:         return chunks
147: 
148:     async def calculate_typing_time(self, file_path: str) -> dict:
149:         try:
150:             with open(file_path, "r") as file:
151:                 lines = file.readlines()
152:             total_chars = sum(len(line.rstrip()) for line in lines)
153:             total_lines = len(lines)
154:             empty_lines = sum(1 for line in lines if not line.strip())
155:             non_empty_lines = total_lines - empty_lines
156: 
157:             avg_char_time = (self.typing_speed["min"] + self.typing_speed["max"]) / 2
158:             char_typing_time = total_chars * avg_char_time
159: 
160:             expected_mistakes = int(total_chars * self.typing_speed["mistake_rate"])
161:             mistake_time = expected_mistakes * (0.2 + 0.1)
162: 
163:             avg_line_break = sum(self.typing_speed["line_break"]) / 2
164:             line_break_time = non_empty_lines * avg_line_break
165:             empty_line_time = empty_lines * (avg_line_break * 0.5)
166: 
167:             total_time = char_typing_time + mistake_time + line_break_time + empty_line_time
168: 
169:             timing_details = {
170:                 "total_time_seconds": round(total_time, 2),
171:                 "total_time_formatted": self._format_time(total_time),
172:                 "breakdown": {
173:                     "characters": {"count": total_chars, "time_seconds": round(char_typing_time, 2)},
174:                     "lines": {"total": total_lines, "empty": empty_lines, "non_empty": non_empty_lines,
175:                               "time_seconds": round(line_break_time + empty_line_time, 2)},
176:                     "expected_mistakes": {"count": expected_mistakes, "time_seconds": round(mistake_time, 2)},
177:                     "typing_speed": {"chars_per_second": round(1 / avg_char_time, 2),
178:                                      "avg_pause_between_lines": round(avg_line_break, 2)},
179:                 },
180:             }
181:             logger.info(f"Estimated typing time: {timing_details['total_time_formatted']}")
182:             self.text_box.value += (
183:                 f"Estimated typing time: {timing_details['total_time_formatted']}\n"
184:                 f"Total characters: {total_chars}\n"
185:                 f"Total lines: {total_lines}\n"
186:                 f"Expected mistakes: {expected_mistakes}\n"
187:             )
188:             return timing_details
189: 
190:         except FileNotFoundError:
191:             logger.error(f"File not found: {file_path}")
192:             self.text_box.value += f"Error: File not found: {file_path}\n"
193:             return None
194:         except Exception as e:
195:             logger.error(f"Error calculating typing time: {e}")
196:             self.text_box.value += f"Error calculating typing time: {e}\n"
197:             return None
198: 
199:     def _format_time(self, seconds: float) -> str:
200:         hours = int(seconds // 3600)
201:         minutes = int((seconds % 3600) // 60)
202:         remaining_seconds = int(seconds % 60)
203:         if hours > 0:
204:             return f"{hours}h {minutes}m {remaining_seconds}s"
205:         elif minutes > 0:
206:             return f"{minutes}m {remaining_seconds}s"
207:         else:
208:             return f"{remaining_seconds}s"
209: 
210:     async def simulate_typing(self, file_path: Optional[str] = None):
211:         if self.simulation_mode == "Tab Switching Only":
212:             self.text_box.value += "Tab switching only mode selected. Skipping typing simulation...\n"
213:             return
214:         elif self.simulation_mode in ["Typing Only", "Hybrid"]:
215: 
216:             chunks = self._split_file_into_chunks(file_path, chunk_size=50)
217:             for i, chunk in enumerate(chunks):
218:                 chunk_text = "".join(chunk)
219:                 await self._simulate_code_typing_from_lines(chunk_text, i)
220:                 await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
221:         else:
222:             self.text_box.value += "Unknown simulation mode selected.\n"
223: 
224:     async def _simulate_code_typing_from_lines(self, text: str, chunk_index: int):
225:         lines = text.splitlines(keepends=True)
226:         original_indents = {i: len(line) - len(line.lstrip()) for i, line in enumerate(lines)}
227:         self.text_box.value += f"Typing chunk {chunk_index + 1}...\n"
228:         for i, line in enumerate(lines):
229:             if not self.loop_flag:
230:                 break
231:             line = " " * original_indents.get(i, 0) + line.strip()
232:             if not line:
233:                 pyautogui.press("enter")
234:                 await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
235:                 continue
236:             await self._type_line_with_simulation(line, i)
237:             await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
238: 
239:     async def _type_line_with_simulation(self, line: str, line_num: int):
240:         if self.formatter:
241:             line = self.formatter.format_line(line)
242:         for char in line:
243:             if not self.loop_flag:
244:                 break
245:             if random.random() < self.typing_speed["mistake_rate"]:
246:                 await self._simulate_typing_mistake(char)
247:             self._type_character(char)
248:             await asyncio.sleep(random.uniform(self.typing_speed["min"], self.typing_speed["max"]))
249:         pyautogui.press("enter")
250:         logger.info(f"Typed line: {line}")
251: 
252:     async def _simulate_typing_mistake(self, correct_char: str):
253:         wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
254:         pyautogui.write(wrong_char)
255:         await asyncio.sleep(0.2)
256:         pyautogui.press("backspace")
257:         await asyncio.sleep(0.1)
258: 
259:     def _type_character(self, char: str):
260:         if char == "\t":
261:             pyautogui.press("tab")
262:         elif char == "\n":
263:             pyautogui.press("enter")
264:         else:
265:             pyautogui.write(char)
266: 
267:     def switch_window(self):
268:         app = self.app_switcher.get_random_running_app()
269:         if app:
270:             if self.app_switcher.focus_application(app):
271:                 self.text_box.value += f"Switched to {app['name']}\n"
272:                 logger.info(f"Switched to {app['name']}")
273:             else:
274:                 self.text_box.value += f"Failed to switch to {app['name']}\n"
275:                 logger.error(f"Failed to switch to {app['name']}")
276:         else:
277:             self.text_box.value += "No configured applications running\n"
278:             logger.warning("No configured applications running")
279: 
280:     async def _simulate_random_actions(self):
281:         while self.loop_flag:
282:             actions = [
283:                 self._random_cursor_move,
284:                 self._random_scroll,
285:                 self._middle_click,
286:                 self._window_switch_action,
287:             ]
288:             for action in actions:
289:                 if not self.loop_flag:
290:                     break
291:                 await action()
292:             await asyncio.sleep(random.uniform(0.3, 0.7))
293: 
294:     async def _random_cursor_move(self):
295:         x = random.randint(100, 1000)
296:         y = random.randint(100, 1000)
297:         pyautogui.moveTo(x, y, duration=0.5)
298:         logger.info(f"Moved cursor to ({x}, {y})")
299: 
300:     async def _random_scroll(self):
301:         scroll_amount = random.randint(-100, 100)
302:         pyautogui.scroll(scroll_amount)
303:         logger.info(f"Scrolled {scroll_amount}")
304:         await asyncio.sleep(0.5)
305:         pyautogui.move(100, 50, duration=0.5)
306:         logger.info("Moved mouse relatively by (100, 50).")
307:         await asyncio.sleep(0.5)
308:         pyautogui.move(-50, -25, duration=0.5)
309:         logger.info("Moved mouse relatively by (-50, -25).")
310:         await asyncio.sleep(0.5)
311: 
312:     async def _middle_click(self):
313:         if random.random() < 0.3:
314:             pyautogui.click(button="middle")
315:             logger.info("Middle clicked")
316: 
317:     async def _window_switch_action(self):
318:         if random.random() < 0.2:
319:             self.switch_window()
320:             await asyncio.sleep(0.5)
321: 
322:     async def _cleanup_simulation(self):
323:         await asyncio.sleep(0.5)
324: 
325:     def _handle_simulation_end(self):
326:         self.loop_flag = False
327:         self.mouse_controller.stop()
328:         self.text_box.value += "Simulation ended\n"
329:         logger.info("Simulation ended")
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
  3: import tempfile
  4: import platform
  5: import subprocess
  6: import sys
  7: from typing import Optional
  8: import toga
  9: from toga.style import Pack
 10: from toga.style.pack import COLUMN, ROW, CENTER
 11: from toga.colors import rgb
 12: from .actions import ActionSimulator
 13: from .key_handler import GlobalKeyHandler
 14: from .logging_config import get_log_path, setup_file_logging, logger
 15: from .path_utils import log_environment_info, get_log_path
 16: 
 17: log_environment_info()
 18: 
 19: 
 20: class CodeSimulator(toga.App):
 21:     def __init__(self):
 22:         super().__init__(
 23:             formal_name="Code Simulator",
 24:             app_id="com.example.codesimulator"
 25:         )
 26: 
 27:         self.selected_file = None
 28: 
 29:     async def show_debug_info(self, widget):
 30: 
 31: 
 32:         info = {
 33:             "OS": platform.system(),
 34:             "OS Version": platform.version(),
 35:             "Python Version": platform.python_version(),
 36:             "App Directory": os.path.dirname(os.path.abspath(__file__)),
 37:             "Current Directory": os.getcwd(),
 38:             "Log File": get_log_path(),
 39:             "Is Packaged": getattr(sys, 'frozen', False),
 40:             "Executable": sys.executable
 41:         }
 42: 
 43: 
 44:         self.text_box.value = "--- Debug Information ---\n\n"
 45:         for key, value in info.items():
 46:             self.text_box.value += f"{key}: {value}\n"
 47: 
 48: 
 49:         log_environment_info()
 50: 
 51:         self.text_box.value += "\nDetailed debug information has been logged to the log file.\n"
 52: 
 53:     async def view_console_logs(self, widget):
 54: 
 55:         try:
 56:             if platform.system() == "Darwin":
 57: 
 58:                 process = subprocess.Popen(
 59:                     ["log", "show", "--predicate", "process == 'Code Simulator'", "--last", "1h"],
 60:                     stdout=subprocess.PIPE,
 61:                     stderr=subprocess.PIPE,
 62:                     text=True
 63:                 )
 64:                 stdout, stderr = process.communicate(timeout=5)
 65: 
 66:                 if stdout:
 67:                     self.text_box.value = "Recent Console Logs:\n\n" + stdout
 68:                 else:
 69:                     self.text_box.value = "No recent console logs found.\n"
 70:                     if stderr:
 71:                         self.text_box.value += f"Error: {stderr}\n"
 72:             else:
 73:                 self.text_box.value = "Console log viewing only supported on macOS."
 74:         except Exception as e:
 75:             self.text_box.value = f"Error viewing console logs: {e}"
 76: 
 77:     async def view_logs(self, widget):
 78: 
 79: 
 80: 
 81:         setup_file_logging()
 82: 
 83: 
 84:         log_path = get_log_path()
 85: 
 86: 
 87:         self.text_box.value = "Log Information\n"
 88:         self.text_box.value += "=============\n\n"
 89:         self.text_box.value += f"Log file location: {log_path}\n\n"
 90: 
 91: 
 92:         logger.info("Test log message from View Logs button")
 93: 
 94: 
 95:         if not os.path.exists(log_path):
 96:             self.text_box.value += f"❌ Log file still not found after write attempt!\n\n"
 97: 
 98: 
 99:             try:
100:                 log_dir = os.path.dirname(log_path)
101:                 test_file_path = os.path.join(log_dir, "test_write.txt")
102:                 with open(test_file_path, 'w') as f:
103:                     f.write("Test write")
104:                 self.text_box.value += f"✓ Successfully created test file at: {test_file_path}\n"
105:                 os.remove(test_file_path)
106:             except Exception as e:
107:                 self.text_box.value += f"❌ Could not write test file: {e}\n"
108:                 self.text_box.value += "This suggests a permissions issue or the directory doesn't exist\n"
109: 
110: 
111:             self.text_box.value += "\nEnvironment Information:\n"
112:             self.text_box.value += f"Working directory: {os.getcwd()}\n"
113:             self.text_box.value += f"Home directory: {os.path.expanduser('~')}\n"
114:             self.text_box.value += f"App directory: {os.path.dirname(__file__)}\n"
115:             self.text_box.value += f"Python executable: {sys.executable}\n"
116:             self.text_box.value += f"Is packaged: {getattr(sys, 'frozen', False)}\n"
117: 
118: 
119:             self.text_box.value += "\nTry looking for logs in these locations:\n"
120:             self.text_box.value += f"1. {os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')}\n"
121:             self.text_box.value += f"2. {tempfile.gettempdir()}\n"
122: 
123:             return
124: 
125: 
126:         file_size = os.path.getsize(log_path)
127:         last_modified = os.path.getmtime(log_path)
128:         import datetime
129:         mod_time = datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
130: 
131:         self.text_box.value += f"Log file size: {file_size} bytes\n"
132:         self.text_box.value += f"Last modified: {mod_time}\n\n"
133: 
134: 
135:         try:
136:             with open(log_path, 'r') as f:
137: 
138:                 if file_size > 10000:
139:                     self.text_box.value += f"Log file is large. Showing last portion...\n\n"
140:                     f.seek(max(0, file_size - 10000))
141: 
142:                     f.readline()
143:                     content = f.read()
144:                 else:
145:                     content = f.read()
146: 
147: 
148:             self.text_box.value += "Log Content:\n"
149:             self.text_box.value += "===========\n\n"
150:             self.text_box.value += content
151: 
152:         except Exception as e:
153:             self.text_box.value += f"❌ Error reading log file: {e}\n"
154: 
155:     def startup(self):
156: 
157:         from .logging_config import setup_file_logging
158:         setup_file_logging()
159: 
160: 
161:         self.setup_ui()
162:         self.setup_components()
163:         logger.info("Application started successfully.")
164: 
165:     def setup_ui(self):
166: 
167:         self.colors = {
168:             'primary': rgb(60, 120, 200),
169:             'accent': rgb(60, 180, 100),
170:             'danger': rgb(220, 70, 70),
171:             'background': rgb(250, 250, 252),
172:             'card': rgb(255, 255, 255),
173:             'text': rgb(50, 50, 50),
174:             'text_light': rgb(120, 120, 120)
175:         }
176: 
177: 
178:         main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
179: 
180: 
181:         header = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color=self.colors['primary']))
182:         title = toga.Label(
183:             "Code Simulator",
184:             style=Pack(
185:                 font_size=24,
186:                 font_weight="bold",
187:                 padding=5,
188:                 color=rgb(255, 255, 255),
189:                 text_align=CENTER
190:             )
191:         )
192:         subtitle = toga.Label(
193:             "Select mode and code file, then start simulation",
194:             style=Pack(
195:                 font_size=14,
196:                 padding=(0, 5, 5, 5),
197:                 color=rgb(220, 220, 220),
198:                 text_align=CENTER
199:             )
200:         )
201: 
202:         header.add(title)
203:         header.add(subtitle)
204:         main_box.add(header)
205: 
206: 
207:         content = toga.Box(style=Pack(direction=ROW, padding=10))
208: 
209: 
210:         left_column = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))
211: 
212: 
213:         mode_label = toga.Label(
214:             "Simulation Mode:",
215:             style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
216:         )
217:         self.simulation_modes = ["Typing Only", "Tab Switching Only", "Hybrid"]
218:         self.mode_selector = toga.Selection(
219:             items=self.simulation_modes,
220:             value=self.simulation_modes[2],
221:             style=Pack(padding=(0, 0, 20, 0))
222:         )
223: 
224:         view_logs_button = toga.Button(
225:             "View Logs",
226:             on_press=self.view_logs,
227:             style=Pack(padding=5, background_color=self.colors['accent'], color=rgb(255, 255, 255))
228:         )
229:         debug_info_button = toga.Button(
230:             "Debug Info",
231:             on_press=self.show_debug_info,
232:             style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
233:         )
234: 
235: 
236:         console_logs_button = toga.Button(
237:             "View Console Logs",
238:             on_press=self.view_console_logs,
239:             style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
240:         )
241:         left_column.add(console_logs_button)
242:         left_column.add(debug_info_button)
243:         left_column.add(view_logs_button)
244:         left_column.add(mode_label)
245:         left_column.add(self.mode_selector)
246: 
247: 
248:         file_label = toga.Label(
249:             "Selected File:",
250:             style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
251:         )
252:         self.file_display = toga.Label(
253:             "Using default resources/code files",
254:             style=Pack(padding=(0, 0, 10, 0), color=self.colors['text_light'])
255:         )
256:         choose_file_button = toga.Button(
257:             "Choose File",
258:             on_press=self.choose_file,
259:             style=Pack(padding=5, background_color=self.colors['accent'], color=rgb(255, 255, 255))
260:         )
261:         left_column.add(file_label)
262:         left_column.add(self.file_display)
263:         left_column.add(choose_file_button)
264: 
265: 
266:         button_box = toga.Box(style=Pack(direction=ROW, padding=(20, 0, 10, 0)))
267:         self.start_button = toga.Button(
268:             "Start Simulation",
269:             on_press=self.start_simulation,
270:             style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
271:         )
272:         self.stop_button = toga.Button(
273:             "Stop Simulation",
274:             on_press=self.stop_simulation,
275:             style=Pack(padding=5, background_color=self.colors['danger'], color=rgb(255, 255, 255)),
276:             enabled=False
277:         )
278:         button_box.add(self.start_button)
279:         button_box.add(toga.Box(style=Pack(flex=1)))
280:         button_box.add(self.stop_button)
281:         left_column.add(button_box)
282: 
283: 
284:         info_box = toga.Box(style=Pack(direction=COLUMN, padding=(20, 0, 0, 0)))
285:         info_label = toga.Label(
286:             "Keyboard Shortcuts:",
287:             style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
288:         )
289:         info_text = toga.Label(
290:             "⌘+S: Start Simulation\n⌘+X: Stop Simulation",
291:             style=Pack(color=self.colors['text_light'])
292:         )
293:         info_box.add(info_label)
294:         info_box.add(info_text)
295:         left_column.add(info_box)
296: 
297: 
298:         right_column = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=2))
299:         output_label = toga.Label(
300:             "Simulation Log:",
301:             style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
302:         )
303:         self.text_box = toga.MultilineTextInput(
304:             readonly=True,
305:             style=Pack(flex=1, background_color=rgb(245, 245, 250))
306:         )
307:         right_column.add(output_label)
308:         right_column.add(self.text_box)
309: 
310: 
311:         content.add(left_column)
312:         content.add(right_column)
313: 
314: 
315:         main_box.add(content)
316: 
317: 
318:         self.main_window = toga.MainWindow(title=self.formal_name)
319:         self.main_window.content = main_box
320: 
321: 
322:         cmd_s = toga.Command(
323:             self.start_simulation,
324:             "Start Simulation",
325:             shortcut=toga.Key.MOD_1 + "s"
326:         )
327:         cmd_x = toga.Command(
328:             self.stop_simulation,
329:             "Stop Simulation",
330:             shortcut=toga.Key.MOD_1 + "x"
331:         )
332:         self.commands.add(cmd_s, cmd_x)
333:         self.main_window.show()
334: 
335:     def setup_components(self):
336:         self.action_simulator = ActionSimulator(self.text_box, self)
337:         self.key_handler = GlobalKeyHandler(self, self.action_simulator)
338:         self.simulation_task = None
339: 
340:     async def choose_file(self, widget):
341: 
342:         dialog = toga.OpenFileDialog(
343:             title="Select a Code File",
344:             file_types=["txt"]
345:         )
346:         file_paths = await self.main_window.dialog(dialog)
347:         if file_paths:
348: 
349:             self.selected_file = file_paths[0]
350: 
351:             filename = os.path.basename(self.selected_file)
352:             self.file_display.text = f"Selected: {filename}"
353:             logger.info(f"Selected file: {self.selected_file}")
354:         else:
355:             self.selected_file = None
356:             self.file_display.text = "Using default resources/code files"
357:             logger.info("No file selected; using default.")
358: 
359:     async def start_simulation(self, widget):
360:         if not self.action_simulator.loop_flag:
361:             try:
362:                 self.text_box.value = "🚀 Starting simulation...\n"
363:                 self.update_button_states(running=True)
364:                 self.action_simulator.loop_flag = True
365: 
366: 
367:                 selected_mode = self.mode_selector.value
368:                 self.action_simulator.simulation_mode = selected_mode
369:                 self.text_box.value += f"▶️ Mode: {selected_mode}\n"
370: 
371: 
372:                 if self.selected_file and selected_mode in ["Typing Only", "Hybrid"]:
373:                     file_to_use = self.selected_file
374:                     filename = os.path.basename(file_to_use)
375:                     self.text_box.value += f"📄 Using selected file: {filename}\n"
376:                 else:
377:                     file_to_use = None
378:                     self.text_box.value += "📄 Using default code samples\n"
379: 
380:                 if not self.simulation_task:
381:                     self.text_box.value += "⏳ Calculating typing time...\n"
382:                     self.simulation_task = asyncio.create_task(self.run_continuous_simulation(file_to_use))
383:                 logger.info("Simulation started successfully.")
384:             except Exception as e:
385:                 logger.error(f"Error starting simulation: {e}")
386:                 await self.stop_simulation(widget)
387: 
388:     async def run_continuous_simulation(self, file_to_use: Optional[str]):
389:         try:
390:             while self.action_simulator.loop_flag:
391: 
392:                 next_file = file_to_use if file_to_use else self.action_simulator.get_next_code_file()
393:                 if not next_file:
394:                     self.text_box.value += "❌ No code files found in resources/code directory.\n"
395:                     await asyncio.sleep(2)
396:                     continue
397: 
398: 
399:                 if self.action_simulator.simulation_mode in ["Typing Only", "Hybrid"]:
400:                     await self.action_simulator.calculate_typing_time(next_file)
401: 
402: 
403:                 if self.action_simulator.simulation_mode == "Typing Only":
404:                     self.text_box.value += "⌨️ Simulating typing...\n"
405:                     await self.action_simulator.simulate_typing(next_file)
406:                 elif self.action_simulator.simulation_mode == "Tab Switching Only":
407:                     self.text_box.value += "🔄 Switching between applications...\n"
408:                     self.action_simulator.switch_window()
409:                     await asyncio.sleep(2)
410:                 elif self.action_simulator.simulation_mode == "Hybrid":
411:                     self.text_box.value += "⌨️ Simulating typing...\n"
412:                     await self.action_simulator.simulate_typing(next_file)
413:                     self.text_box.value += "🔄 Switching between applications...\n"
414:                     self.action_simulator.switch_window()
415:                     await asyncio.sleep(2)
416: 
417:                 filename = os.path.basename(next_file)
418:                 self.text_box.value += f"\n✅ Finished simulating file: {filename}\n"
419:                 self.text_box.value += "🔄 Cycle completed. Restarting...\n\n"
420:                 await asyncio.sleep(2)
421:         except asyncio.CancelledError:
422:             self.text_box.value += "⏹️ Simulation task cancelled.\n"
423:         except Exception as e:
424:             self.text_box.value += f"❌ Error during simulation: {str(e)}\n"
425:             logger.error(f"Error in continuous simulation: {e}")
426:             self.stop_simulation(None)
427: 
428:     async def stop_simulation(self, widget):
429:         if self.action_simulator.loop_flag:
430:             try:
431:                 self.text_box.value += "⏹️ Stopping simulation...\n"
432:                 self.action_simulator.loop_flag = False
433:                 self.update_button_states(running=False)
434:                 if self.simulation_task:
435:                     self.simulation_task.cancel()
436:                     self.simulation_task = None
437:                 logger.info("Simulation stopped successfully.")
438:             except Exception as e:
439:                 logger.error(f"Error stopping simulation: {e}")
440: 
441:     def update_button_states(self, running: bool):
442:         self.start_button.enabled = not running
443:         self.stop_button.enabled = running
444: 
445: 
446: def main():
447:     return CodeSimulator()
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
