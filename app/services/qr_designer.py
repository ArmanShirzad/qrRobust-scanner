"""Advanced QR code designer with logos, colors, and styling."""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer, 
    SquareModuleDrawer, 
    CircleModuleDrawer,
    GappedSquareModuleDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask
)
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import os


class ModuleDrawerType(str, Enum):
    """QR code module drawer types."""
    SQUARE = "square"
    ROUNDED = "rounded"
    CIRCLE = "circle"
    GAPPED_SQUARE = "gapped_square"


class ColorMaskType(str, Enum):
    """QR code color mask types."""
    SOLID = "solid"
    RADIAL_GRADIENT = "radial_gradient"
    SQUARE_GRADIENT = "square_gradient"
    HORIZONTAL_GRADIENT = "horizontal_gradient"
    VERTICAL_GRADIENT = "vertical_gradient"


class QRCodeDesigner:
    """Advanced QR code designer with logos, colors, and styling."""
    
    def __init__(self):
        self.default_size = 300
        self.default_border = 4
        self.default_error_correction = qrcode.constants.ERROR_CORRECT_M
    
    def create_qr_code(
        self,
        data: str,
        size: int = 300,
        border: int = 4,
        error_correction: str = "M",
        fill_color: str = "#000000",
        back_color: str = "#FFFFFF",
        module_drawer: str = "square",
        color_mask: str = "solid",
        logo_path: Optional[str] = None,
        logo_size: Optional[int] = None,
        logo_position: str = "center",
        background_image: Optional[str] = None,
        corner_radius: int = 0,
        custom_styling: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom styled QR code.
        
        Args:
            data: QR code data
            size: QR code size in pixels
            border: Border size
            error_correction: Error correction level (L, M, Q, H)
            fill_color: Foreground color
            back_color: Background color
            module_drawer: Module drawer type
            color_mask: Color mask type
            logo_path: Path to logo image
            logo_size: Logo size (auto-calculated if None)
            logo_position: Logo position (center, top-left, etc.)
            background_image: Path to background image
            corner_radius: Corner radius for rounded modules
            custom_styling: Additional custom styling options
        
        Returns:
            Dict with QR code image data and metadata
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=self._get_error_correction(error_correction),
                box_size=10,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create styled image
            img = self._create_styled_image(
                qr, size, fill_color, back_color, 
                module_drawer, color_mask, corner_radius
            )
            
            # Add logo if provided
            if logo_path and os.path.exists(logo_path):
                img = self._add_logo(img, logo_path, logo_size, logo_position)
            
            # Add background if provided
            if background_image and os.path.exists(background_image):
                img = self._add_background(img, background_image)
            
            # Apply custom styling
            if custom_styling:
                img = self._apply_custom_styling(img, custom_styling)
            
            # Convert to base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "image_data": img_base64,
                "image_format": "PNG",
                "size": img.size,
                "metadata": {
                    "data": data,
                    "error_correction": error_correction,
                    "module_drawer": module_drawer,
                    "color_mask": color_mask,
                    "has_logo": logo_path is not None,
                    "has_background": background_image is not None,
                    "custom_styling": custom_styling is not None
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "data": data,
                    "error_correction": error_correction,
                    "module_drawer": module_drawer,
                    "color_mask": color_mask
                }
            }
    
    def _get_error_correction(self, level: str) -> int:
        """Get error correction constant."""
        levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        return levels.get(level.upper(), qrcode.constants.ERROR_CORRECT_M)
    
    def _create_styled_image(
        self, 
        qr, 
        size: int, 
        fill_color: str, 
        back_color: str,
        module_drawer: str,
        color_mask: str,
        corner_radius: int
    ) -> Image.Image:
        """Create styled QR code image."""
        
        # Get module drawer
        drawer = self._get_module_drawer(module_drawer, corner_radius)
        
        # Get color mask
        color_mask_obj = self._get_color_mask(fill_color, back_color, color_mask)
        
        # Create image
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=drawer,
            color_mask=color_mask_obj
        )
        
        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        return img
    
    def _get_module_drawer(self, drawer_type: str, corner_radius: int):
        """Get module drawer instance."""
        drawers = {
            "square": SquareModuleDrawer(),
            "rounded": RoundedModuleDrawer(radius_ratio=corner_radius / 10.0),
            "circle": CircleModuleDrawer(),
            "gapped_square": GappedSquareModuleDrawer()
        }
        return drawers.get(drawer_type, SquareModuleDrawer())
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _get_color_mask(self, fill_color: str, back_color: str, mask_type: str):
        """Get color mask instance."""
        # Convert hex colors to RGB tuples
        fill_rgb = self._hex_to_rgb(fill_color)
        back_rgb = self._hex_to_rgb(back_color)
        
        masks = {
            "solid": SolidFillColorMask(back_color=back_rgb, front_color=fill_rgb),
            "radial_gradient": RadialGradiantColorMask(
                back_color=back_rgb, 
                center_color=fill_rgb,
                edge_color=self._darken_color(fill_color, 0.3)
            ),
            "square_gradient": SquareGradiantColorMask(
                back_color=back_rgb,
                center_color=fill_rgb,
                edge_color=self._darken_color(fill_color, 0.3)
            ),
            "horizontal_gradient": HorizontalGradiantColorMask(
                back_color=back_rgb,
                left_color=fill_rgb,
                right_color=self._darken_color(fill_color, 0.3)
            ),
            "vertical_gradient": VerticalGradiantColorMask(
                back_color=back_rgb,
                top_color=fill_rgb,
                bottom_color=self._darken_color(fill_color, 0.3)
            )
        }
        return masks.get(mask_type, SolidFillColorMask(back_color=back_rgb, front_color=fill_rgb))
    
    def _darken_color(self, color: str, factor: float) -> Tuple[int, int, int]:
        """Darken a hex color by a factor and return RGB tuple."""
        if color.startswith('#'):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return (r, g, b)
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _add_logo(
        self, 
        qr_img: Image.Image, 
        logo_path: str, 
        logo_size: Optional[int], 
        position: str
    ) -> Image.Image:
        """Add logo to QR code."""
        try:
            logo = Image.open(logo_path)
            
            # Convert to RGBA if needed
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Calculate logo size (20% of QR code size if not specified)
            if logo_size is None:
                logo_size = int(qr_img.size[0] * 0.2)
            
            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create a white background for the logo
            logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
            logo_bg.paste(logo, ((logo_size - logo.size[0]) // 2, (logo_size - logo.size[1]) // 2), logo)
            
            # Calculate position
            qr_width, qr_height = qr_img.size
            logo_width, logo_height = logo_bg.size
            
            if position == "center":
                x = (qr_width - logo_width) // 2
                y = (qr_height - logo_height) // 2
            elif position == "top-left":
                x = qr_width // 4
                y = qr_height // 4
            elif position == "top-right":
                x = (qr_width * 3) // 4 - logo_width
                y = qr_height // 4
            elif position == "bottom-left":
                x = qr_width // 4
                y = (qr_height * 3) // 4 - logo_height
            elif position == "bottom-right":
                x = (qr_width * 3) // 4 - logo_width
                y = (qr_height * 3) // 4 - logo_height
            else:
                x = (qr_width - logo_width) // 2
                y = (qr_height - logo_height) // 2
            
            # Paste logo onto QR code
            qr_img.paste(logo_bg, (x, y), logo_bg)
            
            return qr_img
            
        except Exception as e:
            print(f"Error adding logo: {e}")
            return qr_img
    
    def _add_background(self, qr_img: Image.Image, background_path: str) -> Image.Image:
        """Add background image to QR code."""
        try:
            background = Image.open(background_path)
            background = background.convert('RGBA')
            
            # Resize background to match QR code size
            background = background.resize(qr_img.size, Image.Resampling.LANCZOS)
            
            # Create composite image
            composite = Image.alpha_composite(background, qr_img)
            
            return composite
            
        except Exception as e:
            print(f"Error adding background: {e}")
            return qr_img
    
    def _apply_custom_styling(self, img: Image.Image, styling: Dict[str, Any]) -> Image.Image:
        """Apply custom styling to the image."""
        try:
            # Add border
            if styling.get("border_width", 0) > 0:
                border_color = styling.get("border_color", "#000000")
                border_width = styling.get("border_width", 10)
                
                # Create new image with border
                new_size = (img.size[0] + border_width * 2, img.size[1] + border_width * 2)
                bordered_img = Image.new('RGBA', new_size, border_color)
                bordered_img.paste(img, (border_width, border_width))
                img = bordered_img
            
            # Add shadow
            if styling.get("shadow", False):
                shadow_offset = styling.get("shadow_offset", 5)
                shadow_color = styling.get("shadow_color", "#000000")
                shadow_opacity = styling.get("shadow_opacity", 0.3)
                
                # Create shadow
                shadow_img = Image.new('RGBA', 
                    (img.size[0] + shadow_offset * 2, img.size[1] + shadow_offset * 2), 
                    (0, 0, 0, 0))
                
                # Draw shadow
                shadow_draw = ImageDraw.Draw(shadow_img)
                shadow_draw.rectangle(
                    [shadow_offset, shadow_offset, 
                     img.size[0] + shadow_offset, img.size[1] + shadow_offset],
                    fill=shadow_color
                )
                
                # Composite with original image
                img = Image.alpha_composite(shadow_img, img)
            
            # Add text
            if styling.get("text"):
                text = styling["text"]
                text_color = styling.get("text_color", "#000000")
                text_size = styling.get("text_size", 20)
                text_position = styling.get("text_position", "bottom")
                
                # Create text image
                text_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", text_size)
                except:
                    font = ImageFont.load_default()
                
                # Get text size
                bbox = text_draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Calculate position
                if text_position == "top":
                    x = (img.size[0] - text_width) // 2
                    y = 10
                elif text_position == "bottom":
                    x = (img.size[0] - text_width) // 2
                    y = img.size[1] - text_height - 10
                else:  # center
                    x = (img.size[0] - text_width) // 2
                    y = (img.size[1] - text_height) // 2
                
                # Draw text
                text_draw.text((x, y), text, fill=text_color, font=font)
                
                # Composite with original image
                img = Image.alpha_composite(img, text_img)
            
            return img
            
        except Exception as e:
            print(f"Error applying custom styling: {e}")
            return img
    
    def get_available_styles(self) -> Dict[str, Any]:
        """Get available styling options."""
        return {
            "module_drawers": [drawer.value for drawer in ModuleDrawerType],
            "color_masks": [mask.value for mask in ColorMaskType],
            "error_corrections": ["L", "M", "Q", "H"],
            "logo_positions": ["center", "top-left", "top-right", "bottom-left", "bottom-right"],
            "text_positions": ["top", "center", "bottom"],
            "default_colors": {
                "fill_colors": ["#000000", "#1a1a1a", "#333333", "#666666", "#999999"],
                "back_colors": ["#FFFFFF", "#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA"]
            },
            "gradient_colors": {
                "blue": ["#1e3c72", "#2a5298"],
                "green": ["#11998e", "#38ef7d"],
                "purple": ["#667eea", "#764ba2"],
                "orange": ["#f093fb", "#f5576c"],
                "red": ["#ff9a9e", "#fecfef"]
            }
        }
    
    def validate_design_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate design options and return cleaned options."""
        cleaned = {}
        
        # Include data parameter
        if "data" in options:
            cleaned["data"] = options["data"]
        
        # Validate size
        size = options.get("size", self.default_size)
        cleaned["size"] = max(100, min(2000, int(size)))
        
        # Validate border
        border = options.get("border", self.default_border)
        cleaned["border"] = max(0, min(20, int(border)))
        
        # Validate error correction
        error_correction = options.get("error_correction", "M")
        if error_correction.upper() in ["L", "M", "Q", "H"]:
            cleaned["error_correction"] = error_correction.upper()
        else:
            cleaned["error_correction"] = "M"
        
        # Validate colors
        cleaned["fill_color"] = self._validate_color(options.get("fill_color", "#000000"))
        cleaned["back_color"] = self._validate_color(options.get("back_color", "#FFFFFF"))
        
        # Validate module drawer
        module_drawer = options.get("module_drawer", "square")
        if module_drawer in [drawer.value for drawer in ModuleDrawerType]:
            cleaned["module_drawer"] = module_drawer
        else:
            cleaned["module_drawer"] = "square"
        
        # Validate color mask
        color_mask = options.get("color_mask", "solid")
        if color_mask in [mask.value for mask in ColorMaskType]:
            cleaned["color_mask"] = color_mask
        else:
            cleaned["color_mask"] = "solid"
        
        # Validate corner radius
        corner_radius = options.get("corner_radius", 0)
        cleaned["corner_radius"] = max(0, min(10, int(corner_radius)))
        
        # Validate logo options
        if options.get("logo_path"):
            cleaned["logo_path"] = options["logo_path"]
            cleaned["logo_size"] = max(20, min(200, int(options.get("logo_size", 60))))
            logo_position = options.get("logo_position", "center")
            if logo_position in ["center", "top-left", "top-right", "bottom-left", "bottom-right"]:
                cleaned["logo_position"] = logo_position
            else:
                cleaned["logo_position"] = "center"
        
        # Validate custom styling
        if options.get("custom_styling"):
            styling = options["custom_styling"]
            cleaned_styling = {}
            
            if styling.get("border_width"):
                cleaned_styling["border_width"] = max(0, min(50, int(styling["border_width"])))
                cleaned_styling["border_color"] = self._validate_color(styling.get("border_color", "#000000"))
            
            if styling.get("shadow"):
                cleaned_styling["shadow"] = True
                cleaned_styling["shadow_offset"] = max(1, min(20, int(styling.get("shadow_offset", 5))))
                cleaned_styling["shadow_color"] = self._validate_color(styling.get("shadow_color", "#000000"))
                cleaned_styling["shadow_opacity"] = max(0.1, min(1.0, float(styling.get("shadow_opacity", 0.3))))
            
            if styling.get("text"):
                cleaned_styling["text"] = str(styling["text"])[:100]  # Limit text length
                cleaned_styling["text_color"] = self._validate_color(styling.get("text_color", "#000000"))
                cleaned_styling["text_size"] = max(10, min(50, int(styling.get("text_size", 20))))
                text_position = styling.get("text_position", "bottom")
                if text_position in ["top", "center", "bottom"]:
                    cleaned_styling["text_position"] = text_position
                else:
                    cleaned_styling["text_position"] = "bottom"
            
            if cleaned_styling:
                cleaned["custom_styling"] = cleaned_styling
        
        return cleaned
    
    def _validate_color(self, color: str) -> str:
        """Validate and normalize color."""
        if not color.startswith('#'):
            color = '#' + color
        
        # Remove any invalid characters but keep the #
        color = '#' + ''.join(c for c in color[1:] if c in '0123456789ABCDEFabcdef')
        
        # Ensure proper length
        if len(color) == 4:  # #RGB
            color = f"#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}"
        elif len(color) != 7:  # #RRGGBB
            color = "#000000"
        
        return color.upper()


# Global designer instance
qr_designer = QRCodeDesigner()
