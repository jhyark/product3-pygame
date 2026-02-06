# 리소스 수집 게임
# 플레이어가 맵을 돌아다니며 리소스를 수집하고 적을 피하는 게임

import pygame
import random
import sys
import math
import os

# 게임 설정
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Pygame 초기화
pygame.init()
pygame.mixer.init()

# 화면 설정
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("리소스 수집 게임")
fullscreen = False

# 배경 음악 로드
for ext in ['bgm.mp3', 'bgm.wav', 'music.mp3', 'music.wav']:
    bgm_path = os.path.join(os.path.dirname(__file__), ext)
    if os.path.isfile(bgm_path):
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # -1은 무한 반복
            break
        except Exception:
            continue

# 클럭 및 폰트 설정
clock = pygame.time.Clock()

# 한국어 폰트 설정 (시스템 폰트 사용) - 크기 40% 축소
try:
    # Windows 시스템 폰트 사용
    font_large = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 29)  # 48 * 0.6
    font_medium = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 19)  # 32 * 0.6
    font_small = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 14)   # 24 * 0.6
except:
    try:
        # 대체 폰트 시도
        font_large = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 29)
        font_medium = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 19)
        font_small = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 14)
    except:
        try:
            # 기본 시스템 폰트 시도
            font_large = pygame.font.SysFont("arial", 29)
            font_medium = pygame.font.SysFont("arial", 19)
            font_small = pygame.font.SysFont("arial", 14)
        except:
            # 최후의 수단: 기본 폰트
            font_large = pygame.font.Font(None, 29)
            font_medium = pygame.font.Font(None, 19)
            font_small = pygame.font.Font(None, 14)

# 텍스트 그리기 함수
def draw_text(surface, text, font, color, x, y, align="center"):
    """화면에 텍스트를 그리는 함수"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "left":
        text_rect.left = x
        text_rect.top = y
    elif align == "right":
        text_rect.right = x
        text_rect.top = y
    else:  # center
        text_rect.center = (x, y)
        
    surface.blit(text_surface, text_rect)

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self, player_type="player1"):
        super().__init__()
        self.width = 30
        self.height = 30
        self.speed = 5
        self.player_type = player_type  # "player1" 또는 "player2"
        
        # 플레이어 타입에 따라 다른 이미지 로드
        if player_type == "player1":
            image_file = 'yy.png'
        else:  # player2
            image_file = 'cc.png'
            
        # 두 플레이어 모두 같은 크기로 설정 (50% 키움)
        self.width = 75
        self.height = 75
            
        try:
            image_path = os.path.join(os.path.dirname(__file__), image_file)
            if os.path.isfile(image_path):
                loaded_image = pygame.image.load(image_path).convert_alpha()
                
                # 이미지를 설정된 크기로 조정 (원본 그대로 사용)
                self.image = pygame.transform.smoothscale(loaded_image, (self.width, self.height))
                            
            else:
                # 파일이 없으면 기본 원형 이미지 사용
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                if player_type == "player1":
                    pygame.draw.circle(self.image, BLUE, (self.width//2, self.height//2), self.width//2)
                else:
                    pygame.draw.circle(self.image, GREEN, (self.width//2, self.height//2), self.width//2)
                pygame.draw.circle(self.image, WHITE, (self.width//2, self.height//2), self.width//2-3, 2)
        except Exception:
            # 이미지 로드 실패 시 기본 원형 이미지 사용
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            if player_type == "player1":
                pygame.draw.circle(self.image, BLUE, (self.width//2, self.height//2), self.width//2)
            else:
                pygame.draw.circle(self.image, GREEN, (self.width//2, self.height//2), self.width//2)
            pygame.draw.circle(self.image, WHITE, (self.width//2, self.height//2), self.width//2-3, 2)
        
        self.rect = self.image.get_rect()
        # 플레이어 위치를 다르게 설정 (좌우 바뀜)
        if player_type == "player1":
            self.rect.centerx = SCREEN_WIDTH // 2 + 50
            self.rect.centery = SCREEN_HEIGHT // 2
        else:  # player2
            self.rect.centerx = SCREEN_WIDTH // 2 - 50
            self.rect.centery = SCREEN_HEIGHT // 2
        
        # 플레이어 상태
        self.resources_collected = 0
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_time = 0
        
    def update(self):
        """플레이어 업데이트"""
        keys = pygame.key.get_pressed()
        
        # 이동 처리 - 플레이어 타입에 따라 다른 키 사용
        dx = dy = 0
        
        if self.player_type == "player1":
            # 플레이어1: 화살표키 사용
            if keys[pygame.K_LEFT]:
                dx = -self.speed
            if keys[pygame.K_RIGHT]:
                dx = self.speed
            if keys[pygame.K_UP]:
                dy = -self.speed
            if keys[pygame.K_DOWN]:
                dy = self.speed
        else:  # player2
            # 플레이어2: WASD 키 사용
            if keys[pygame.K_a]:
                dx = -self.speed
            if keys[pygame.K_d]:
                dx = self.speed
            if keys[pygame.K_w]:
                dy = -self.speed
            if keys[pygame.K_s]:
                dy = self.speed
            
        # 대각선 이동 시 속도 조정
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        self.rect.x += dx
        self.rect.y += dy
        
        # 화면 경계 체크
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
        # 무적 시간 업데이트
        if self.invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False
                
        # 무적 상태일 때 깜빡임 효과
        if self.invulnerable and self.invulnerable_time % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
            
    def take_damage(self):
        """데미지 받기"""
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_time = 120  # 2초간 무적 (60 FPS 기준)
            return True
        return False

# 리소스 클래스
class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y, resource_type):
        super().__init__()
        self.resource_type = resource_type
        self.value = 1
        
        # 리소스 타입에 따른 색상과 크기 설정
        if resource_type == "gold":
            self.color = GOLD
            self.size = 15
            self.value = 3
        elif resource_type == "crystal":
            self.color = PURPLE
            self.size = 12
            self.value = 2
        elif resource_type == "energy":
            self.color = YELLOW
            self.size = 10
            self.value = 1
        else:  # 기본 리소스
            self.color = GREEN
            self.size = 8
            self.value = 1
            
        # 리소스 이미지 생성
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(self.image, WHITE, (self.size, self.size), self.size-2, 2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        # 애니메이션을 위한 변수
        self.animation_time = 0
        self.original_size = self.size
        
    def update(self):
        """리소스 애니메이션 업데이트"""
        self.animation_time += 1
        # 부드러운 상하 움직임
        bounce = math.sin(self.animation_time * 0.1) * 2
        self.rect.y += int(bounce)

# 적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 25
        self.height = 25
        self.speed = random.uniform(1, 3)
        
        # 적 이미지 생성 (삼각형)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [
            (self.width//2, 0),
            (0, self.height),
            (self.width, self.height)
        ])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        # 이동 방향
        self.direction = random.uniform(0, 2 * math.pi)
        self.change_direction_time = random.randint(60, 180)
        self.current_time = 0
        
    def update(self):
        """적 업데이트"""
        self.current_time += 1
        
        # 주기적으로 방향 변경
        if self.current_time >= self.change_direction_time:
            self.direction = random.uniform(0, 2 * math.pi)
            self.change_direction_time = random.randint(60, 180)
            self.current_time = 0
            
        # 이동
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        
        self.rect.x += dx
        self.rect.y += dy
        
        # 화면 경계에서 튕기기
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction = math.pi - self.direction
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.direction = -self.direction
            
        # 화면 경계 내로 유지
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# 파워업 클래스
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.duration = 300  # 5초 (60 FPS 기준)
        
        # 파워업 타입에 따른 설정
        if power_type == "speed":
            self.color = ORANGE
            self.size = 20
        elif power_type == "shield":
            self.color = LIGHT_BLUE
            self.size = 18
        else:  # 기본 파워업
            self.color = WHITE
            self.size = 15
            
        # 파워업 이미지 생성
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(self.image, BLACK, (self.size, self.size), self.size-3, 3)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        self.animation_time = 0
        
    def update(self):
        """파워업 애니메이션 업데이트"""
        self.animation_time += 1
        # 회전 효과
        bounce = math.sin(self.animation_time * 0.2) * 3
        self.rect.y += int(bounce)

# 게임 초기화
all_sprites = pygame.sprite.Group()
resources = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# 플레이어들 생성
player1 = Player("player1")  # yy.png 사용, 화살표키 조작
player2 = Player("player2")  # cc.png 사용, WASD 키 조작
all_sprites.add(player1)
all_sprites.add(player2)

# 게임 상태
score = 0
game_over = False
level = 1
spawn_timer = 0

def spawn_resource():
    """리소스 생성"""
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    
    # 리소스 타입 랜덤 선택
    resource_types = ["gold", "crystal", "energy", "basic"]
    weights = [0.1, 0.2, 0.3, 0.4]  # 가중치
    resource_type = random.choices(resource_types, weights=weights)[0]
    
    resource = Resource(x, y, resource_type)
    all_sprites.add(resource)
    resources.add(resource)

def spawn_enemy():
    """적 생성"""
    # 화면 가장자리에서 생성
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, SCREEN_WIDTH)
        y = -25
    elif side == "bottom":
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT + 25
    elif side == "left":
        x = -25
        y = random.randint(0, SCREEN_HEIGHT)
    else:  # right
        x = SCREEN_WIDTH + 25
        y = random.randint(0, SCREEN_HEIGHT)
        
    enemy = Enemy(x, y)
    all_sprites.add(enemy)
    enemies.add(enemy)

def spawn_powerup():
    """파워업 생성"""
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    
    power_types = ["speed", "shield"]
    power_type = random.choice(power_types)
    
    powerup = PowerUp(x, y, power_type)
    all_sprites.add(powerup)
    powerups.add(powerup)

# 초기 리소스와 적 생성
for _ in range(15):
    spawn_resource()
    
for _ in range(3):
    spawn_enemy()

# 메인 게임 루프
running = True
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # 전체화면 토글
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    # 전체화면 크기 가져오기
                    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                else:
                    screen = pygame.display.set_mode((1000, 700))
                    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
            elif event.key == pygame.K_r and game_over:
                # 게임 재시작
                game_over = False
                score = 0
                level = 1
                
                # 모든 스프라이트 제거
                for sprite in all_sprites:
                    sprite.kill()
                resources.empty()
                enemies.empty()
                powerups.empty()
                
                # 플레이어들 재생성
                player1 = Player("player1")
                player2 = Player("player2")
                all_sprites.add(player1)
                all_sprites.add(player2)
                
                # 초기 리소스와 적 생성
                for _ in range(15):
                    spawn_resource()
                for _ in range(3):
                    spawn_enemy()
    
    # 게임 상태 업데이트
    if not game_over:
        all_sprites.update()
        spawn_timer += 1
        
        # 리소스 수집 체크 - 두 플레이어 모두
        collected_resources1 = pygame.sprite.spritecollide(player1, resources, True)
        for resource in collected_resources1:
            score += resource.value
            player1.resources_collected += resource.value
            
        collected_resources2 = pygame.sprite.spritecollide(player2, resources, True)
        for resource in collected_resources2:
            score += resource.value
            player2.resources_collected += resource.value
            
        # 파워업 수집 체크 - 두 플레이어 모두
        collected_powerups1 = pygame.sprite.spritecollide(player1, powerups, True)
        for powerup in collected_powerups1:
            if powerup.power_type == "speed":
                player1.speed = min(player1.speed + 1, 8)
            elif powerup.power_type == "shield":
                player1.lives += 1
                
        collected_powerups2 = pygame.sprite.spritecollide(player2, powerups, True)
        for powerup in collected_powerups2:
            if powerup.power_type == "speed":
                player2.speed = min(player2.speed + 1, 8)
            elif powerup.power_type == "shield":
                player2.lives += 1
                
        # 적과 충돌 체크 - 두 플레이어 모두
        enemy_hits1 = pygame.sprite.spritecollide(player1, enemies, False)
        if enemy_hits1:
            if player1.take_damage():
                if player1.lives <= 0:
                    game_over = True
                    
        enemy_hits2 = pygame.sprite.spritecollide(player2, enemies, False)
        if enemy_hits2:
            if player2.take_damage():
                if player2.lives <= 0:
                    game_over = True
                    
        # 리소스 재생성
        if len(resources) < 10 and random.random() < 0.02:
            spawn_resource()
            
        # 적 재생성
        if len(enemies) < 2 + level and random.random() < 0.01:
            spawn_enemy()
            
        # 파워업 생성
        if len(powerups) < 2 and random.random() < 0.005:
            spawn_powerup()
            
        # 레벨 업
        if score > level * 50:
            level += 1
            # 레벨업 시 추가 적 생성
            for _ in range(2):
                spawn_enemy()
    
    # 화면 그리기
    screen.fill(DARK_GREEN)  # 배경색
    
    # 그리드 패턴 그리기 (선택사항)
    for x in range(0, SCREEN_WIDTH, 50):
        pygame.draw.line(screen, (0, 80, 0), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 50):
        pygame.draw.line(screen, (0, 80, 0), (0, y), (SCREEN_WIDTH, y), 1)
    
    all_sprites.draw(screen)
    
    # UI 그리기 - 플레이어별 점수를 상단 좌우에 표시
    # 플레이어2 정보 (상단 왼쪽)
    draw_text(screen, f"루카 점수: {player2.resources_collected}", font_medium, WHITE, 20, 20, "left")
    draw_text(screen, f"생명: {player2.lives}", font_medium, WHITE, 20, 45, "left")
    
    # 플레이어1 정보 (상단 오른쪽)
    draw_text(screen, f"요셉 점수: {player1.resources_collected}", font_medium, WHITE, SCREEN_WIDTH - 20, 20, "right")
    draw_text(screen, f"생명: {player1.lives}", font_medium, WHITE, SCREEN_WIDTH - 20, 45, "right")
    
    # 레벨 정보 (상단 중앙)
    draw_text(screen, f"레벨: {level}", font_medium, WHITE, SCREEN_WIDTH // 2, 20)
    
    # 게임 오버 화면
    if game_over:
        draw_text(screen, "Game Over!", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        draw_text(screen, f"최종 점수:", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        draw_text(screen, f"{score}", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15)
        draw_text(screen, f"요셉 리소스: {player1.resources_collected}", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
        draw_text(screen, f"루카 리소스: {player2.resources_collected}", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35)
        draw_text(screen, "R키를 눌러 재시작", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
    
    # 조작법 안내
    draw_text(screen, "조작법: 요셉(화살표키) 루카(WASD) F11(전체화면)", font_small, WHITE, 20, SCREEN_HEIGHT - 20, "left")
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
